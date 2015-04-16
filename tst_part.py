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

# for Kazoo logging
import logging
logging.basicConfig() 

DEBUG = True 

# string of Zk server addresses
servers = ""
# Kazoo Zk clients
clients = []

num_write = 100
key_len = 10
value_len = 2

num_clients = 10
num_thread = num_clients

test_root = "/tst/"

test_db = {}

failed_writes = 0

lock = RLock()

def state_listener(state):
    if state == KazooState.LOST:
        print "State: LOST"
    elif state == KazooState.SUSPENDED:
        print "State: SUSPENDED"
    else:
        print "State: CONNECTED" 


def test():
    print "ZK partition test."
    try:
        setup_servers()
        get_servers_addrs()
        setup_clients()
        write()
        read()
        print "OK."
    finally:
        shutdown()

def setup_clients():
    global clients 
    for i in range(0,num_clients):
        zk = KazooClient(servers)
        zk.add_listener(state_listener)
        zk.start()
        clients.append(zk)
        print "Connected to: " + zk._connection._socket.getpeername()[0]
    clients[0].ensure_path(test_root)
    
def get_servers_addrs():
    parser = block.setup_parser()
    opts = parser.parse_args(args=["status"])
    config = block.load_config(opts)
    b = block.get_blockade(config)
    containers = b.status()
    
    global servers
    for c in containers:
        servers += c.ip_address
        servers += ":2181,"
    servers.strip(",")
    
def setup_servers():
    # Blockade up
    parser = block.setup_parser()
    opts = parser.parse_args(args=["up"])
    block.cmd_up(opts)
    
    # Zk start
    subp.call(["./zk_start.sh"])
    
def shutdown():
    # Blocakde destroy
    parser = block.setup_parser()
    opts = parser.parse_args(args=["destroy"])
    block.cmd_destroy(opts)
    
def write():
    p = ThreadPool(num_write)

    # partition one random server from the others
    partition(random.choice(["zk1","zk2","zk3"]))
    
    # print partition status
    parser = block.setup_parser()
    opts = parser.parse_args(args=["status"])
    block.cmd_status(opts)
    
    for i in p.map(_issue_writes, clients):
        pass
   
    #time.sleep(2)
        
    p.close()
    p.join()
    
    join_partition()

def partition(srv):
    # Blockade partition
    print "Partitioning " + srv
    parser = block.setup_parser()
    opts = parser.parse_args(args=["partition", srv])
    block.cmd_partition(opts)
    
def join_partition():
    # Blockade join
    print "Joining partitions"
    parser = block.setup_parser()
    opts = parser.parse_args(args=["join"])
    block.cmd_join(opts)

def _issue_writes(zkc):
    for i in range(1, num_write+1):
        key = test_root + ''.join(random.choice(string.ascii_letters) for i in range(key_len))
        value = ''.join(random.choice(string.ascii_letters) for i in range(value_len))
        #cmd = "S " + key + " " + str(value)
        #_print(cmd)
        try:
            ret = zkc.create(key, value.encode()) # or: create_async
        except:
            with lock: 
                global failed_writes
                failed_writes += 1
            try:
                print "Failed write on " + zkc._connection._socket.getpeername()[0]
            except: # at this point the socket object might be null
                print "Failed write on some server"
        else:
            test_db[key] = value.encode()

def read():
    print "Reading " + str(len(test_db.keys())) + " keys, out of " + str((num_clients * num_write))
    assert len(test_db.keys()) == ((num_clients * num_write) - failed_writes)
    for key in test_db.keys():
        cmd = "G " + key
        data, stat = clients[0].get(key)
        assert data == test_db[key]

def _print(str):
    if DEBUG:
        print str


if __name__=="__main__":
    test()

