@echo off

setlocal
set PYTHONPATH=../lib/
@echo on

python generic.py %*

@echo off
endlocal
