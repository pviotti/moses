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

All experiments have been performed on a single machine running Ubuntu 15.10.  

Follow the [instructions on Docker's website](https://docs.docker.com/linux/step_one/) to install Docker.  

Preliminary setup:

    sudo apt-get install python-pip sshpass 

Blockade:

    sudo pip install blockade

Final check:

    docker info
    sudo blockade -h


## Usage

Each folder contains the test files for a specific store. 
Once in a certain folder, you can issue the following commands.  
To build the needed Docker images and install dependencies:

    make build

To run the write test with network partitions:

    make run
	

## License

Apache 2.0
