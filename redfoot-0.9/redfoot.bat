@echo off

setlocal
set PYTHONPATH=./lib/
@echo on

python ./lib/redfoot/server.py %*

@echo off
endlocal
