# Moses

> "Lift up your staff, and stretch out your hand over the sea and divide it"

Experiments on network partitions with [Blockade][1], as in the [Jepsen][2] series.  

For the moment, the game is about:

 1. partitioning the network
 2. issuing writes to cluster's servers on both sides of the partition
 3. healing the partition
 4. verifying that each acknowledged write's value is actually present into the store
    by issuing read operations on random servers of the cluster


 [1]: https://github.com/dcm-oss/blockade
 [2]: https://aphyr.com/tags/jepsen

## Host machine setup

Generic tools setup:

    sudo apt-get update && sudo apt-get upgrade
    sudo apt-get install language-pack-en
    sudo locale-gen en_GB.UTF-8
    sudo echo LANGUAGE=en_GB.UTF-8 >> /etc/environment
    sudo echo LC_ALL=en_GB.UTF-8 >> /etc/environment
    sudo apt-get install zsh tshark git lxctl lxc python-pip sshpass ipython \
      python-kazoo
    sudo chsh ubuntu -s /bin/zsh


Docker:

    sudo su
    wget -qO- https://get.docker.com/ | sh
    sudo usermod -aG docker ubuntu

Blockade:

    sudo pip install blockade
    sudo echo 'DOCKER_OPTS="-e lxc ${DOCKER_OPTS}"' >> /etc/default/docker


Final check (after rebooting):

    docker info
    sudo blockade -h


## License

Apache 2.0
