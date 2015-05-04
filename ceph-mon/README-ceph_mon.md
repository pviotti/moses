# Moses vs Ceph Monitor KVS

Testing a modified version of Ceph Monitor 0.94 that includes a simple 
in-memory key-value store against network faults.  

## Containers setup

Docker image setup: 

    docker build -t viotti/ceph:v1 .
    
Blockade

    blockade up
    ./ceph_start.sh
    ./ceph_watch.sh # issue mon_status command
