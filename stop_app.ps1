# Medical Store Application Stopper

Write-Host "Stopping Medical Store Application..." -ForegroundColor Cyan
Write-Host ""

# Stop backend server process (Python/uvicorn)
Write-Host "Stopping backend server..." -ForegroundColor Yellow
Get-Process -Name python -ErrorAction SilentlyContinue | Stop-Process -Force

# Stop frontend server process (Node.js)
Write-Host "Stopping frontend server..." -ForegroundColor Yellow
Get-Process -Name node -ErrorAction SilentlyContinue | Stop-Process -Force

Write-Host ""
Write-Host "Medical Store Application has been stopped." -ForegroundColor Green
Write-Host ""
Write-Host "Press any key to exit..." -ForegroundColor Gray
$null = $Host.UI.RawUI.ReadKey("NoEcho,IncludeKeyDown")