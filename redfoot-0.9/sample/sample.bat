@echo off

setlocal
set PYTHONPATH=../lib/
@echo on

rem python ./sample.py -P /2000/10/redfoot/ -l sample.rdf
python ./sample.py -P / -l sample.rdf

@echo off
endlocal
