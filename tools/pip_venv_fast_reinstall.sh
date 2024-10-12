#!/bin/bash

# Just replace the package in venv
PROJECT=TEMPLATE
DIR=$(find venv/ -type d -name $PROJECT | tr -d '\n')
rm -rf $DIR
cp -r $PROJECT $DIR
