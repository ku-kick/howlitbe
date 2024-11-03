#!/bin/bash

# Builds all bash scripts
# Stub structure MUST comply the following requirements
# 1. Each directory DOES contain Dockerfile
# 2. Each directory's name IS used as a resulting docker image
# 3. Each directory contains the necessary files for running a container

HERE=$(realpath $(dirname ${BASH_SOURCE[0]}))
LIST=$(find $HERE -mindepth 1 -maxdepth 1 -type d | xargs realpath | xargs -n 1 basename)

for i in $LIST ; do 
	if [ ! -f $i/Dockerfile ] ; then
		echo ERROR: file $i/Dockerfile does not exist
		exit 1
	fi
done
echo Will build the following images: $LIST
