#!/bin/bash

read -d '' -r -a servers <<<`blockade status | tr -s " " | cut -d " " -f4 | tail -n +2`

watch -n 2 "echo srvr | nc ${servers[0]} 2181; echo; echo srvr | nc ${servers[1]} 2181; echo; echo srvr | nc ${servers[2]} 2181; echo; echo srvr | nc ${servers[3]} 2181; echo; echo srvr | nc ${servers[4]} 2181;"
