@echo off

setlocal
set PYTHONPATH=../lib/
@echo on

python ./sample.py -P /2000/10/redfoot/ -l sample.rdf

@echo off
endlocal
