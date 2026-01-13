# ============================================
# Stop All Services - RAG Application
# ============================================

Write-Host ""
Write-Host "=" * 50 -ForegroundColor Red
Write-Host "  Stopping RAG Application Services" -ForegroundColor Red
Write-Host "=" * 50 -ForegroundColor Red
Write-Host ""

# Stop all Python processes (Backend)
Write-Host "[1/3] Stopping Backend (Python)..." -ForegroundColor Yellow
try {
    taskkill /F /IM python.exe 2>$null
    if ($LASTEXITCODE -eq 0) {
        Write-Host "✓ Backend stopped successfully" -ForegroundColor Green
    }
    else {
        Write-Host "✓ No backend processes found" -ForegroundColor Gray
    }
}
catch {
    Write-Host "✓ No backend processes found" -ForegroundColor Gray
}

# Stop all Node processes (Frontend)
Write-Host "[2/3] Stopping Frontend (Node)..." -ForegroundColor Yellow
try {
    taskkill /F /IM node.exe 2>$null
    if ($LASTEXITCODE -eq 0) {
        Write-Host "✓ Frontend stopped successfully" -ForegroundColor Green
    }
    else {
        Write-Host "✓ No frontend processes found" -ForegroundColor Gray
    }
}
catch {
    Write-Host "✓ No frontend processes found" -ForegroundColor Gray
}

# Verify ports are free
Write-Host "[3/3] Verifying ports are free..." -ForegroundColor Yellow
$port8000 = Get-NetTCPConnection -LocalPort 8000 -ErrorAction SilentlyContinue
$port5173 = Get-NetTCPConnection -LocalPort 5173 -ErrorAction SilentlyContinue

if ($port8000) {
    Write-Host "⚠ Port 8000 still in use (PID: $($port8000.OwningProcess))" -ForegroundColor Yellow
}
else {
    Write-Host "✓ Port 8000 is free" -ForegroundColor Green
}

if ($port5173) {
    Write-Host "⚠ Port 5173 still in use (PID: $($port5173.OwningProcess))" -ForegroundColor Yellow
}
else {
    Write-Host "✓ Port 5173 is free" -ForegroundColor Green
}

Write-Host ""
Write-Host "=" * 50 -ForegroundColor Red
Write-Host "  All Services Stopped!" -ForegroundColor Red
Write-Host "  No API calls will be made to Groq" -ForegroundColor Red
Write-Host "=" * 50 -ForegroundColor Red
Write-Host ""
