#!/bin/bash

read -d '' -r -a ips <<<`blockade status | tr -s " " | cut -d " " -f4 | tail -n +2`

SSH_OPTS="-o StrictHostKeyChecking=no -o UserKnownHostsFile=/dev/null"

cp _zoo.cfg zoo.cfg

end=$(( ${#ips[@]} - 1 ))
for i in $(seq 0 $end)
do
	sed -i "s/zk$i/${ips[$i]}/g" zoo.cfg
done

for i in $(seq 0 $end)
do
    sshpass -p 'root' scp $SSH_OPTS zoo.cfg root@${ips[$i]}:/opt/zookeeper/conf/ 2>/dev/null
    sshpass -p 'root' ssh $SSH_OPTS root@${ips[$i]} "mkdir -p /tmp/zookeeper; echo $(( $i + 1 )) > /tmp/zookeeper/myid" 2>/dev/null
    sshpass -p 'root' ssh $SSH_OPTS root@${ips[$i]} "/opt/zookeeper/bin/zkServer.sh start" 2>/dev/null
done

