@echo off

setlocal
set PYTHONPATH=../../../
@echo on

python all.py -p 8000 %*

@echo off
endlocal
