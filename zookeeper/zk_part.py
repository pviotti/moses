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

num_write = 100
key_len = 10
value_len = 2
num_clients = 10
num_thread = num_clients
test_root = "/tst/"


def _get_blockade_cmd(cmd):
    parser = block.setup_parser()
    return parser.parse_args(args=cmd)


class ZkPartitioner:

    def __init__(self):
        self.servers = ""    # string of Zk server addresses
        self.clients = []    # Kazoo Zk clients
        self.num_servers = 0
        self.test_db = {}
        self.failed_writes = 0
        self.lock = RLock()

    def run(self):
        logging.info("ZooKeeper partition test.")
        try:
            self.setup_servers()
            self.get_servers_addrs()
            self.setup_clients()
            self.write()
            self.read()
        finally:
            self.shutdown()
            
    def setup_servers(self):
        logging.info("Setup servers...")
        block.cmd_up(_get_blockade_cmd(["up"]))
        subp.call(["./zk_start.sh"])
        
    def get_servers_addrs(self):
        # Get server addresses through Blockade
        b = block.get_blockade(block.load_config(None), _get_blockade_cmd(["up"]))
        containers = b.status()
        
        for c in containers:
            self.servers += c.ip_address
            self.servers += ":2181,"
            self.num_servers += 1
        self.servers = self.servers.strip(",")
        #print servers

    def setup_clients(self):
        logging.info("Setup clients...")
        for i in range(0, num_clients):
            zk = KazooClient(self.servers)
            zk.add_listener(self._state_listener)
            zk.start()
            self.clients.append(zk)
            logging.info("Client " + str(i) + " connected to: " + zk._connection._socket.getpeername()[0])
        self.clients[0].ensure_path(test_root)   # Create test path
        
    def write(self):
        # partition one random server from the others
        self.partition("zk" + str(random.randint(1, self.num_servers)) + "," +
                 "zk" + str(random.randint(1, self.num_servers)) )
        # print partition status
        block.cmd_status(_get_blockade_cmd(["status"]))
        
        p = ThreadPool(num_thread)
        p.map(self._issue_writes, self.clients)
       
        #time.sleep(2)
        p.close()
        p.join()
        self.join_partition()
        
    def partition(self, srv):
        """ Blockade partition """
        logging.info("Partitioning " + srv)
        block.cmd_partition(_get_blockade_cmd(["partition", srv]))
        
    def join_partition(self):
        """ Blockade join """
        logging.info("Joining partitions")
        block.cmd_join(_get_blockade_cmd(["join"]))

    def _issue_writes(self, zkc):
        for i in range(1, num_write+1):
            key = test_root + ''.join(random.choice(string.ascii_letters) for i in range(key_len))
            value = ''.join(random.choice(string.ascii_letters) for i in range(value_len))
            try:
                ret = zkc.create(key, value.encode())
            except:
                with self.lock: 
                    self.failed_writes += 1
                try:
                    logging.debug("Failed write on " + zkc._connection._socket.getpeername()[0])
                except: # at this point the socket object might be null
                    logging.debug("Failed write on some server")
            else:
                self.test_db[key] = value.encode()

    def read(self):
        logging.info("Reading " + str(len(self.test_db.keys())) + " keys, out of " + str((num_clients * num_write)))
        assert len(self.test_db.keys()) == ((num_clients * num_write) - self.failed_writes)
        for key in self.test_db.keys():
            data, stat = self.clients[random.randint(0,num_clients-1)].get(key)
            assert data == self.test_db[key]
      
    def shutdown(self):
        """ Blockade destroy """
        block.cmd_destroy(_get_blockade_cmd(["destroy"]))

    def _state_listener(self, state):
        if state == KazooState.LOST:
            logging.debug("State: LOST")
        elif state == KazooState.SUSPENDED:
            logging.debug("State: SUSPENDED")
        else:
            logging.debug("State: CONNECTED")


if __name__=="__main__":
    ZkPartitioner().run()
