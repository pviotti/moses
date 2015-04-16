#!/usr/bin/env python
# Simple tool to perform smoke tests on
# Zookeeper during partitions.
# @author: Paolo
# @date: 16/4/2015

import random, string, time
from kazoo.client import KazooClient, KazooState

DEBUG = True 

servers = "localhost:2181,localhost:2182,localhost:2183"

num_write = 50
key_len = 10
max_value = 10000
num_delete = 10

test_db = {}

def state_listener(state):
    if state == KazooState.LOST:
        print "State: LOST"
    elif state == KazooState.SUSPENDED:
        print "State: SUSPENDED"
    else:
        print "State: CONNECTED" 

zk = KazooClient(servers)
zk.add_listener(state_listener)
zk.start()

def test():
    print "ZK partition smoke test"
    tst_set()
    tst_get()
    #tst_list()
    #tst_delete()
    #tst_writeread()
    print "OK."

def tst_set():
    for i in range(1, num_write+1):
        key = "/" + ''.join(random.choice(string.ascii_letters) for i in range(key_len))
        value = ''.join(random.choice(string.ascii_letters) for i in range(key_len))
        test_db[key] = value.encode()
        cmd = "S " + key + " " + str(value)
        _print(cmd)
        ret = zk.create(key, value.encode())
        assert ret == key

def tst_get():
    for key in test_db.keys():
        cmd = "G " + key
        _print(cmd)
        data, stat = zk.get(key)
        _print("R: " + str(data))
        assert data == test_db[key]

def tst_list():
    for server in servers:
        cmd = "L"
        #ret = str(_send_recv(server, cmd))
        _print(ret)
        assert len(ret) > 0
        for key in test_db.keys():
            assert ret.find(key) != -1


def tst_writeread():
    for i in range(1, num_write+1):
        key = ''.join(random.choice(string.ascii_letters) for i in range(key_len))
        value = random.randint(0,max_value)
        cmd = "S " + key + " " + str(value)
        _print(cmd)
        #ret = _send_recv(random.choice(servers), cmd)
        assert ret == b'A'
        _print("R: " + str(ret))
        
        cmd = "G " + key
        _print(cmd)
        #ret = _send_recv(random.choice(servers), cmd)
        _print("R: " + str(ret))
        assert int(ret) == value
        

def _print(str):
    if DEBUG:
        print str


if __name__=="__main__":
    test()

