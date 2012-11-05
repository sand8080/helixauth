#!/bin/sh

DIR="$( cd "$( dirname "$0" )" && pwd )"

#Set environment
export PATH=$DIR/.env/bin:$PATH
export PYTHONPATH=$DIR/src

$DIR/.env/bin/fab -f $DIR/fabfile.py deploy
