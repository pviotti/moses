#!/bin/bash

#kill $(pgrep ceph-mon)

rm -rf test
mkdir -p test

cwd=`pwd`/test
cat > test/conf <<EOF

[global]
pid file = $cwd/\$name.pid
log file = $cwd/\$cluster-\$name.log
run dir = $cwd

[mon]
admin socket = $cwd/\$cluster-\$name.asok
;mon data = $cwd/\$name

debug mon = 5
debug paxos = 20
debug auth = 0
EOF

cd test
rm -f mm
monmaptool --create mm --fsid a7f64266-0894-4f1e-a635-d0aeaca0e993 \
    --add a CEPH0:6789 \
    --add b CEPH1:6789 \
    --add c CEPH2:6789

ceph-mon -c conf -i $1 --mkfs --monmap mm --mon-data $cwd/mon.$1 -k ../keyring
ceph-mon -c conf -i $1 --mon-data $cwd/mon.$1
