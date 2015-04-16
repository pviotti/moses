#!/usr/bin/env python3
# Simple tool to perform concurrency tests on
# Zookpeer.
# @author: Paolo
# @date: 15/4/2015

import random, string, time
from kazoo.client import KazooClient, KazooState
import concurrent.futures

DEBUG = True 

servers = "localhost:2181,localhost:2182,localhost:2183"

num_write = 500
key_len = 10
max_value = 10000

test_db = {}

def state_listener(state):
    if state == KazooState.LOST:
        print("State: LOST")
    elif state == KazooState.SUSPENDED:
        print("State: SUSPENDED")
    else:
        print("State: CONNECTED")

zk = KazooClient(servers)
zk.add_listener(state_listener)
zk.start()

def test():
    print("ZK concurrency test")
    tst_conc()
    tst_get()
    print("OK.")

def tst_conc():
    e = concurrent.futures.ThreadPoolExecutor(num_write)
    for i in e.map(_issue_set, range(1, num_write+1)):
        pass
    e.shutdown(wait=True)

def tst_get():
    for key in test_db.keys():
        cmd = "G " + key
        _print(cmd)
        ret, stat = zk.get(key)
        _print("R: " + str(ret))
        assert ret == test_db[key]

def _issue_set(x):
    key = "/" + ''.join(random.choice(string.ascii_letters) for i in range(key_len))
    value = ''.join(random.choice(string.ascii_letters) for i in range(key_len))
    test_db[key] = value.encode()
    cmd = "S " + key + " " + value
    _print(cmd)
    ret = zk.create(key, value.encode())
    assert ret == key



def _print(str):
    if DEBUG:
        print(str)


if __name__=="__main__":
    test()

