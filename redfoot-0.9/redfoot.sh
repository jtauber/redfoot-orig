#!/bin/sh

PYTHONPATH=../lib/:$PYTHONPATH; export PYTHONPATH

python ./sample.py -P /2000/10/redfoot -l sample.rdf
