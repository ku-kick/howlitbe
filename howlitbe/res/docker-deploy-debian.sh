#!/bin/bash
# Prepares the environment for deploying docker, and starts docker process
# Supposed to be run from an isolated network namespace (Mininet host)

#unshare --mount '/bin/bash -c "mkdir -p /tmp/$1 ;  mount --bind /tmp/$1 /var ; containerd & && dockerd"'

# Handle cgroupfs
cgroupfs-umount
cgroupfs-mount

# Docker uses /var to detect conflicts b/w running docker instanes. Substitude w/ an empty /var directory
D=$1
echo Mountint /var
mkdir -p /tmp/$D
mount --bind /tmp/$D /var
/bin/bash

# Run daemons
containerd &
dockerd
