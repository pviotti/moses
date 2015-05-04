# Moses vs Zookeeper

Testing Zookeeper 3.4.6 against network faults.


## Containers setup

Docker image setup: 

    docker build -t viotti/zk:v1 .
    
Blockade setup:

    blockade up
    ./zk_start.sh
    ./zk_watch.sh # watch cluster status using four letters Zk commands
