#!/bin/bash

read -d '' -r -a ips <<<`sudo blockade status | tr -s " " | cut -d " " -f4 | tail -n +2`

cp _zoo.cfg zoo.cfg

end=$(( ${#ips[@]} - 1 ))
for i in $(seq 0 $end)
do
	sed -i "s/zk$i/${ips[$i]}/g" zoo.cfg
done

for i in $(seq 0 $end)
do
    sshpass -p 'root' scp -o StrictHostKeyChecking=no zoo.cfg root@${ips[$i]}:/opt/zookeeper/conf/ 2>/dev/null
    sshpass -p 'root' ssh -o StrictHostKeyChecking=no root@${ips[$i]} "echo $(( $i + 1 )) > /tmp/myid" 2>/dev/null
    sshpass -p 'root' ssh -o StrictHostKeyChecking=no root@${ips[$i]} "/opt/zookeeper/bin/zkServer.sh start" 2>/dev/null
done
