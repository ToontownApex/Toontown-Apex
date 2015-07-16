@echo off


set APX_KEY=0
set APX_PASS=dA2wEju
set APEX_GS1=127.0.0.1

rem Read the contents of PPYTHON_PATH into %PPYTHON_PATH%:
set /P PPYTHON_PATH=<PPYTHON_PATH

echo xxxxxxxxxxxxxxxxxxxxxxxxxxxxxxx
echo Starting Toontown Apex Client! Please wait.
echo ppython: %PPYTHON_PATH%
echo Username: %APXUsername%
echo Client Agent IP: %APEX_GS1%
echo xxxxxxxxxxxxxxxxxxxxxxxxxxxxxxx

%PPYTHON_PATH% -m toontown.toonbase.ToontownStart
pause
