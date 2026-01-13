# Run Both Frontend and Backend
Write-Host "==================================================" -ForegroundColor Magenta
Write-Host "  RAG Application - Starting All Services" -ForegroundColor Magenta
Write-Host "==================================================" -ForegroundColor Magenta
Write-Host ""

# Start Backend in new terminal
Write-Host "Starting Backend..." -ForegroundColor Green
Start-Process powershell -ArgumentList "-NoExit", "-Command", "cd '$PSScriptRoot\backend'; .\run.ps1"

# Wait a bit for backend to start
Start-Sleep -Seconds 3

# Start Frontend in new terminal
Write-Host "Starting Frontend..." -ForegroundColor Green
Start-Process powershell -ArgumentList "-NoExit", "-Command", "cd '$PSScriptRoot\frontend'; .\run.ps1"

Write-Host ""
Write-Host "==================================================" -ForegroundColor Magenta
Write-Host "  Services Started!" -ForegroundColor Green
Write-Host "  Backend:  http://127.0.0.1:8000" -ForegroundColor Cyan
Write-Host "  Frontend: http://localhost:5173" -ForegroundColor Cyan
Write-Host "  API Docs: http://127.0.0.1:8000/docs" -ForegroundColor Cyan
Write-Host "==================================================" -ForegroundColor Magenta
