@echo off
rem load a webpage over and over again with iexplore.exe then exit
rem this is going to be used in conjuction with some flask based server for fuzzing
:loop
"C:\Program Files (x86)\Internet Explorer\iexplore.exe" http://example.com && timeout 30 && taskkill /F /IM iexplore.exe /T
goto loop
