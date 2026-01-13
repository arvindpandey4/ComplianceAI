# Backend Run Script
Write-Host "Starting RAG Application Backend..." -ForegroundColor Green

# Activate virtual environment if it exists
if (Test-Path ".venv\Scripts\Activate.ps1") {
    Write-Host "Activating virtual environment..." -ForegroundColor Yellow
    & .venv\Scripts\Activate.ps1
} elseif (Test-Path "venv\Scripts\Activate.ps1") {
    Write-Host "Activating virtual environment..." -ForegroundColor Yellow
    & venv\Scripts\Activate.ps1
} else {
    Write-Host "No virtual environment found. Using global Python..." -ForegroundColor Yellow
}

# Run the backend
Write-Host "Starting FastAPI server on http://127.0.0.1:8000" -ForegroundColor Cyan
python -m uvicorn main:app --reload --host 127.0.0.1 --port 8000
