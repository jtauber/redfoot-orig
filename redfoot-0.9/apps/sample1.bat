@echo off

setlocal
set PYTHONPATH=../lib/
@echo on

python ./sample1.py -P /2000/10/redfoot/ -l sample1.rdf %*

@echo off
endlocal
