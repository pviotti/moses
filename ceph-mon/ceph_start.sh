#!/bin/bash

read -d '' -r -a ips <<<`sudo blockade status | tr -s " " | cut -d " " -f4 | tail -n +2`

cp _ceph-mon_start.sh ceph-mon_start.sh

end=$(( ${#ips[@]} - 1 ))
for i in $(seq 0 $end)
do
	sed -i "s/CEPH$i/${ips[$i]}/g" ceph-mon_start.sh
done

for i in $(seq 0 $end)
do
    declare -i myintid=$(($i +97))
    myid=$(printf \\$(printf '%03o' $myintid))
    sshpass -p 'root' scp -o StrictHostKeyChecking=no -o UserKnownHostsFile=/dev/null keyring root@${ips[$i]}:/root/ #2>/dev/null
    sshpass -p 'root' scp -o StrictHostKeyChecking=no -o UserKnownHostsFile=/dev/null ceph-mon_start.sh root@${ips[$i]}:/root/ #2>/dev/null
    sshpass -p 'root' ssh -o StrictHostKeyChecking=no -o UserKnownHostsFile=/dev/null root@${ips[$i]} "bash /root/ceph-mon_start.sh $myid" #2>/dev/null
done
