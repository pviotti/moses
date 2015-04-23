# Moses vs Zookeeper

Testing Zookeeper 3.4.6 against network faults.


## Containers setup

Docker commands

    docker ps
    docker build -t viotti/zk:v1 .
    docker images
    
Blockade

    blockade up
    ./zk_start.sh
    ./zk_watch.sh
