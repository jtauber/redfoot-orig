@echo off

setlocal
set PYTHONPATH=../lib/
@echo on

python ./sample1Main.py %*

@echo off
endlocal
