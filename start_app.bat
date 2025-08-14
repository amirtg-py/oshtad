@echo off
echo Starting Medical Store Application...
echo.

:: Set the project root directory
set PROJECT_ROOT=%~dp0
cd %PROJECT_ROOT%

:: Activate Python virtual environment
echo Activating virtual environment...
if not exist venv (
    echo Creating virtual environment...
    python -m venv venv
)
call venv\Scripts\activate.bat

:: Install backend dependencies
echo Installing backend dependencies...
pip install -r backend\requirements.txt

:: Start backend server in a new window
echo Starting backend server...
:: Wait for MongoDB to be available
powershell -NoProfile -Command "while (-not (Test-NetConnection -ComputerName localhost -Port 27017 -InformationLevel Quiet)) { Write-Host 'Waiting for MongoDB on port 27017...' ; Start-Sleep -Seconds 2 }"
echo MongoDB is up. Starting backend.
start cmd /k "title Backend Server && cd %PROJECT_ROOT% && call venv\Scripts\activate.bat && cd backend && python server.py"

:: Wait for backend to initialize
timeout /t 5 /nobreak

:: Navigate to frontend directory
cd %PROJECT_ROOT%\frontend

:: Install frontend dependencies
echo Installing frontend dependencies...
npm install --force

:: Start frontend server in a new window
echo Starting frontend server...
start cmd /k "title Frontend Server && cd %PROJECT_ROOT%\frontend && npx react-scripts start"

:: Open browser after a delay
timeout /t 10 /nobreak
echo Opening application in browser...
start http://localhost:3000

echo.
echo Medical Store Application is now running!
echo Backend: http://localhost:8000
echo Frontend: http://localhost:3000
echo.
echo Press any key to exit this window. The application will continue running in the other windows.
pause > nul