@echo off

setlocal
set PYTHONPATH=../lib/
echo Usage (example): run module_name
@echo on

python ../lib/redfoot/server.py %*

@echo off
endlocal
