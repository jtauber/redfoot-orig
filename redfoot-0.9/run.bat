@echo off

rem Runs the redfoot server with the SampleUI 

setlocal
set PYTHONPATH=../
@echo on

python server.py -P /2000/10/redfoot -i SampleUI -l sampleui.rdf


@echo off
endlocal
