@echo off

setlocal
set PYTHONPATH=../../lib/
@echo on

python ./neighbours.py $*

@echo off
endlocal


