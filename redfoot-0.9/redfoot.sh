#!/bin/sh

PYTHONPATH=./lib/:$PYTHONPATH; export PYTHONPATH

python ./lib/redfoot/server.py $*

