#!/usr/bin/env python
# Simple tool to perform smoke tests on
# Zookeeper during partitions.
# @author: Paolo
# @date: 16/4/2015

from multiprocessing.pool import ThreadPool
import random, string, time
import subprocess as subp

from kazoo.client import KazooClient, KazooState
from blockade import cli

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

def state_listener(state):
    if state == KazooState.LOST:
        print "State: LOST"
    elif state == KazooState.SUSPENDED:
        print "State: SUSPENDED"
    else:
        print "State: CONNECTED" 


def test():
    print "ZK partition test"
    setup_servers()
    get_servers_addrs()
    setup_clients()
    write()
    read()
    shutdown()
    print "OK."

def setup_clients():
    global clients 
    for i in range(0,num_clients):
        zk = KazooClient(servers)
        zk.add_listener(state_listener)
        zk.start()
        clients.append(zk)
    clients[0].ensure_path(test_root)
    
def get_servers_addrs():
    parser = cli.setup_parser()
    opts = parser.parse_args(args=["status"])
    config = cli.load_config(opts)
    b = cli.get_blockade(config)
    containers = b.status()
    
    global servers
    for c in containers:
        servers += c.ip_address
        servers += ":2181,"
    
def setup_servers():
    # Blockade up
    parser = cli.setup_parser()
    opts = parser.parse_args(args=["up"])
    cli.cmd_up(opts)
    
    # Zk start
    subp.call(["./zk_start.sh"])
    
def shutdown():
    # Blocakde destroy
    parser = cli.setup_parser()
    opts = parser.parse_args(args=["destroy"])
    cli.cmd_destroy(opts)
    
def write():
    p = ThreadPool(num_write)
    for i in p.map(_issue_writes, clients):
        pass
    p.close()
    p.join()
    

def _issue_writes(zkc):
    for i in range(1, num_write+1):
        key = test_root + ''.join(random.choice(string.ascii_letters) for i in range(key_len))
        value = ''.join(random.choice(string.ascii_letters) for i in range(value_len))
        test_db[key] = value.encode()
        #cmd = "S " + key + " " + str(value)
        #_print(cmd)
        ret = zkc.create(key, value.encode())
        assert ret == key

def read():
    for key in test_db.keys():
        cmd = "G " + key
        _print(cmd)
        data, stat = clients[0].get(key)
        _print("R: " + str(data))
        assert data == test_db[key]
        

def _print(str):
    if DEBUG:
        print str


if __name__=="__main__":
    test()

