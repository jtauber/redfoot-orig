@echo off
setlocal
set PYTHONPATH=../
@echo on

rem python %1 -- use this if/when we need to run more than one thing and when we can kick out a usage message... for now...

python server.py


@echo off
endlocal
