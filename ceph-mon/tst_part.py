#!/usr/bin/env python
# Simple tool to perform read-write tests on
# Ceph Mon during partitions.
# @author: Paolo
# @date: 23/4/2015

from multiprocessing.pool import ThreadPool
import random, string, time
import subprocess as subp
from threading import RLock
import socket

from blockade import cli as block

import logging
logging.basicConfig(level=logging.INFO) 

servers = []    # array of Ceph Mon servers' addresses

num_write = 100
key_len = 10
max_value = 10000
num_clients = 10
num_thread = num_clients

test_db = {}

failed_writes = 0
lock = RLock()


def test():
    logging.info("Ceph partition test.")
    try:
        setup_servers()
        get_servers_addrs()
        write()
        time.sleep(3)
        read()
    finally:
        shutdown()
        
def setup_servers():
    logging.info("Setup servers...")
    # Blockade up
    parser = block.setup_parser()
    opts = parser.parse_args(args=["up"])
    block.cmd_up(opts)
    # Ceph start
    subp.call(["./ceph_start.sh"])
    
def get_servers_addrs():
    # Get server addresses through Blockade
    parser = block.setup_parser()
    opts = parser.parse_args(args=["status"])
    config = block.load_config(opts)
    b = block.get_blockade(config)
    containers = b.status()
    
    global servers
    for c in containers:
        servers.append((c.ip_address, 5000))

def write():
    p = ThreadPool(num_write)

    # partition one random server from the others
    partition(random.choice(["ceph1","ceph2","ceph3"]))
    
    # print partition status
    parser = block.setup_parser()
    opts = parser.parse_args(args=["status"])
    block.cmd_status(opts)
    
    for i in p.map(_issue_writes, range(0,num_clients)):
        pass
   
    #time.sleep(2)
    p.close()
    p.join()
    join_partition()
    
def partition(srv):
    # Blockade partition
    logging.info("Partitioning " + srv)
    parser = block.setup_parser()
    opts = parser.parse_args(args=["partition", srv])
    block.cmd_partition(opts)
    
def join_partition():
    # Blockade join
    logging.info("Joining partitions")
    parser = block.setup_parser()
    opts = parser.parse_args(args=["join"])
    block.cmd_join(opts)

def _issue_writes(cli):
    for i in range(1, num_write+1):
        key = ''.join(random.choice(string.ascii_letters) for i in range(key_len))
        value = str(random.randint(0,max_value))
	srv = random.choice(servers)
        try:
            ret = _send_recv(srv, "S " + key + " " + value)
        except:
            with lock: 
                global failed_writes
                failed_writes += 1
            logging.warning("Failed write on " + srv[0])
        else:
            test_db[key] = value.encode()

def _send_recv(host_port, cmd):
    s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    s.settimeout(3)
    s.connect(host_port)
    s.send(cmd.encode())
    return s.recv(10000)

def read():
    logging.info("Reading " + str(len(test_db.keys())) + " keys, out of " + str((num_clients * num_write)))
    assert len(test_db.keys()) == ((num_clients * num_write) - failed_writes)
    for key in test_db.keys():
        srv = random.choice(servers)
        try:
            data = _send_recv(srv, "G " + key)
        except:
	    logging.warning("failed to read " + key + " from " + srv[0])
        else:
            try:
                assert data == test_db[key]
            except AssertionError:
                logging.error("ASSERTION ERROR on " + srv[0] + " of " + key + ": got " + data)
  
def shutdown():
    # Blocakde destroy
    parser = block.setup_parser()
    opts = parser.parse_args(args=["destroy"])
    block.cmd_destroy(opts)


if __name__=="__main__":
    test()

