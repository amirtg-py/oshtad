@echo off
echo Stopping Medical Store Application...

:: Kill backend server process (Python/uvicorn)
echo Stopping backend server...
taskkill /f /im python.exe /t

:: Kill frontend server process (Node.js)
echo Stopping frontend server...
taskkill /f /im node.exe /t

echo.
echo Medical Store Application has been stopped.
echo.
echo Press any key to exit...
pause > nul