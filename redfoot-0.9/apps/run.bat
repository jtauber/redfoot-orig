@echo off

setlocal
set PYTHONPATH=../lib/
echo Usage (example): run_redpage.bat sample3.xml
@echo on

python ../lib/redfoot/server.py %*

@echo off
endlocal
