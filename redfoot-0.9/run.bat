@echo off
rem python %1 -- use this if/when we need to run more than one thing and when we can kick out a usage message... for now... TODO: un hard code the arguments

setlocal
set PYTHONPATH=../
@echo on


python server.py -p 8000 -l ./example.rdf -u http://www.bowstreet.com/2000/08/20 -i PeerEditor


@echo off
endlocal
