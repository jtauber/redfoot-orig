@echo off

setlocal
set PYTHONPATH=../lib/
echo Usage (example): run_.bat foo.xml
@echo on

python ../lib/redfoot/server.py %*

@echo off
endlocal
