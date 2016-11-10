# Moses

> "Lift up your staff, and stretch out your hand over the sea and divide it"

Experiments on network partitions with [Blockade][1], as in the [Jepsen][2] series.  

For the moment, the game is about:

 1. partitioning the network
 2. issuing writes to servers on both sides of the partition
 3. healing the partition
 4. verifying that each acknowledged write's value is actually present into the store
    by invoking read operations on random servers of the cluster


 [1]: https://github.com/dcm-oss/blockade
 [2]: https://aphyr.com/tags/jepsen


## Setup

Requirements:
 
 * [Docker](https://docs.docker.com/engine/getstarted/step_one/) (tested with version 1.12)
 * Blockade 0.3.0 (`sudo pip install blockade==0.3.0`)


Check the setup with the following commands:

    docker info
    blockade -h


## Usage

Each folder contains the test files for a specific store. 
Once in a certain folder, you can issue the following commands.  
To build the Docker images and install the needed dependencies:

    make build

To run the write test with network partitions:

    make run
	

## License

Apache 2.0
