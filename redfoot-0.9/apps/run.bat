@echo off

setlocal
set PYTHONPATH=../lib/
echo Usage (example): run.bat sample1.py
@echo on

python %*

@echo off
endlocal
