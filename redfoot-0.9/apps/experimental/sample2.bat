@echo off

setlocal
set PYTHONPATH=../lib/
@echo on

python ./sample2Main.py %*

@echo off
endlocal
