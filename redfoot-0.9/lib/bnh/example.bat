@echo off

setlocal
set PYTHONPATH=../
@echo on

python example.py -p 8000 %*

@echo off
endlocal
