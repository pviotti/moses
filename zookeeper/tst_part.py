#!/usr/bin/env python
# Simple tool to perform smoke tests on
# Zookeeper during partitions.
# @author: Paolo
# @date: 16/4/2015

from multiprocessing.pool import ThreadPool
import random, string, time
import subprocess as subp
from threading import RLock

from kazoo.client import KazooClient, KazooState
from blockade import cli as block

import logging
logging.basicConfig(level=logging.INFO) 
logging.getLogger("kazoo.client").setLevel(logging.ERROR)

servers = ""    # string of Zk server addresses
clients = []    # Kazoo Zk clients
num_servers = 0

num_write = 100
key_len = 10
value_len = 2
num_clients = 10
num_thread = num_clients
test_root = "/tst/"

test_db = {}

failed_writes = 0
lock = RLock()


def test():
    logging.info("ZK partition test.")
    try:
        setup_servers()
        get_servers_addrs()
        setup_clients()
        write()
        read()
    finally:
        shutdown()
        
def _prepare_blockade_cmd(cmd):
    parser = block.setup_parser()
    return parser.parse_args(args=cmd)
        
def setup_servers():
    logging.info("Setup servers...")
    # Blockade up
    block.cmd_up(_prepare_blockade_cmd(["up"]))
    # Zk start
    subp.call(["./zk_start.sh"])
    
def get_servers_addrs():
    # Get server addresses through Blockade
    config = block.load_config(None)
    b = block.get_blockade(config, _prepare_blockade_cmd(["up"]))
    containers = b.status()
    
    global servers
    global num_servers
    for c in containers:
        servers += c.ip_address
        servers += ":2181,"
        num_servers += 1
    servers = servers.strip(",")
    #print servers

def setup_clients():
    logging.info("Setup clients...")
    global clients 
    for i in range(0, num_clients):
        zk = KazooClient(servers)
        zk.add_listener(state_listener)
        zk.start()
        clients.append(zk)
        logging.info("Client " + str(i) + " connected to: " + zk._connection._socket.getpeername()[0])
    clients[0].ensure_path(test_root)   # Create test path
    
def write():
    p = ThreadPool(num_write)

    # partition one random server from the others
    partition("zk" + str(random.randint(1,num_servers)) + "," +
             "zk" + str(random.randint(1,num_servers)) )
    
    # print partition status
    block.cmd_status(_prepare_blockade_cmd(["status"]))
    
    for i in p.map(_issue_writes, clients):
        pass
   
    #time.sleep(2)
    p.close()
    p.join()
    join_partition()
    
def partition(srv):
    # Blockade partition
    logging.info("Partitioning " + srv)
    block.cmd_partition(_prepare_blockade_cmd(["partition", srv]))
    
def join_partition():
    # Blockade join
    logging.info("Joining partitions")
    parser = block.setup_parser()
    opts = parser.parse_args(args=["join"])
    block.cmd_join(opts)

def _issue_writes(zkc):
    for i in range(1, num_write+1):
        key = test_root + ''.join(random.choice(string.ascii_letters) for i in range(key_len))
        value = ''.join(random.choice(string.ascii_letters) for i in range(value_len))
        try:
            ret = zkc.create(key, value.encode()) # or: create_async
        except:
            with lock: 
                global failed_writes
                failed_writes += 1
            try:
                logging.debug("Failed write on " + zkc._connection._socket.getpeername()[0])
            except: # at this point the socket object might be null
                logging.debug("Failed write on some server")
        else:
            test_db[key] = value.encode()

def read():
    logging.info("Reading " + str(len(test_db.keys())) + " keys, out of " + str((num_clients * num_write)))
    assert len(test_db.keys()) == ((num_clients * num_write) - failed_writes)
    for key in test_db.keys():
        data, stat = clients[0].get(key)
        assert data == test_db[key]
  
def shutdown():
    # Blockade destroy
    block.cmd_destroy(_prepare_blockade_cmd(["destroy"]))

def state_listener(state):
    if state == KazooState.LOST:
        logging.debug("State: LOST")
    elif state == KazooState.SUSPENDED:
        logging.debug("State: SUSPENDED")
    else:
        logging.debug("State: CONNECTED")


if __name__=="__main__":
    test()
