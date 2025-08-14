# Medical Store Application Launcher

Write-Host "Starting Medical Store Application..." -ForegroundColor Cyan
Write-Host ""

# Set the project root directory
$PROJECT_ROOT = $PSScriptRoot
Set-Location $PROJECT_ROOT

# Activate Python virtual environment
Write-Host "Activating virtual environment..." -ForegroundColor Yellow
if (-not (Test-Path "venv")) {
    Write-Host "Creating virtual environment..." -ForegroundColor Yellow
    python -m venv venv
}

# Activate virtual environment
& .\venv\Scripts\Activate.ps1

# Install backend dependencies
Write-Host "Installing backend dependencies..." -ForegroundColor Yellow
pip install -r backend\requirements.txt

# Start backend server in a new window
Write-Host "Starting backend server..." -ForegroundColor Green
# Wait for MongoDB to be available
while (-not (Test-NetConnection -ComputerName localhost -Port 27017 -InformationLevel Quiet)) {
    Write-Host "Waiting for MongoDB on port 27017..."
    Start-Sleep -Seconds 2
}
Write-Host "MongoDB is up. Starting backend."
Start-Process powershell -ArgumentList "-NoExit", "-Command", "Set-Location '$PROJECT_ROOT'; & .\\venv\\Scripts\\Activate.ps1; Set-Location backend; uvicorn server:app --host 0.0.0.0 --port 8000" -WindowStyle Normal

# Wait for backend to initialize
Write-Host "Waiting for backend to initialize..." -ForegroundColor Yellow
Start-Sleep -Seconds 5

# Navigate to frontend directory
Set-Location "$PROJECT_ROOT\frontend"

# Install frontend dependencies
Write-Host "Installing frontend dependencies..." -ForegroundColor Yellow
npm install --force

# Start frontend server in a new window
Write-Host "Starting frontend server..." -ForegroundColor Green
Start-Process powershell -ArgumentList "-NoExit", "-Command", "Set-Location '$PROJECT_ROOT\frontend'; npx react-scripts start" -WindowStyle Normal

# Open browser after a delay
Write-Host "Waiting for frontend to initialize..." -ForegroundColor Yellow
Start-Sleep -Seconds 10
Write-Host "Opening application in browser..." -ForegroundColor Green
Start-Process "http://localhost:3000"

Write-Host ""
Write-Host "Medical Store Application is now running!" -ForegroundColor Cyan
Write-Host "Backend: http://localhost:8000" -ForegroundColor Cyan
Write-Host "Frontend: http://localhost:3000" -ForegroundColor Cyan
Write-Host ""
Write-Host "Press any key to exit this window. The application will continue running in the other windows." -ForegroundColor Gray
$null = $Host.UI.RawUI.ReadKey("NoEcho,IncludeKeyDown")