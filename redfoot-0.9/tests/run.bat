@echo off
setlocal
set PYTHONPATH=../../
@echo on

python parser-tests.py serializer-tests.py

@echo off
endlocal
