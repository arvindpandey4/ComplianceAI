# Frontend Run Script
Write-Host "Starting RAG Application Frontend..." -ForegroundColor Green

# Check if node_modules exists
if (-Not (Test-Path "node_modules")) {
    Write-Host "node_modules not found. Installing dependencies..." -ForegroundColor Yellow
    npm install
}

# Run the frontend
Write-Host "Starting Vite dev server..." -ForegroundColor Cyan
npm run dev
