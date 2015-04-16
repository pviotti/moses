# Moses

> "Lift up your staff, and stretch out your hand over the sea and divide it"

Experiments on network partitions with [Blockade](https://github.com/dcm-oss/blockade).


## Machine setup

Type of machine: small

    sudo apt-get update && sudo apt-get upgrade
    sudo apt-get install language-pack-en
    sudo locale-gen en_GB.UTF-8
    sudo echo LANGUAGE=en_GB.UTF-8 >> /etc/environment
    sudo echo LC_ALL=en_GB.UTF-8 >> /etc/environment
    sudo apt-get install zsh tshark git lxctl lxc python-pip sshpass


Zsh

    sudo su
    chsh ubuntu -s /bin/zsh


Docker

    sudo su
    wget -qO- https://get.docker.com/ | sh
    sudo usermod -aG docker ubuntu

Blockade

    sudo pip install blockade
    sudo echo 'DOCKER_OPTS="-e lxc ${DOCKER_OPTS}"' >> /etc/default/docker
    
    
Final check
    
    sudo reboot
    
    docker info
    sudo blockade -h
    

## Create containers

Docker commands

    docker ps
    docker build -t viotti/zk:v1 .
    docker images
    
Blockade

    blockade up
    ./zk_start.sh
    ./zk_watch.sh
    

## License

Apache 2.0
