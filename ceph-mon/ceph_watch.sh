#!/bin/bash

read -d '' -r -a servers <<<`sudo blockade status | tr -s " " | cut -d " " -f4 | tail -n +2`

watch -n 5 sshpass -p 'root' ssh root@${servers[0]} "ceph -f json-pretty -c /root/test/conf -k /root/keyring --monmap /root/test/mm mon_status"
