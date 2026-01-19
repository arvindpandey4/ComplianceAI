# ============================================
# Stop All Services - RAG Application
# ============================================

Write-Host ""
Write-Host ("=" * 50) -ForegroundColor Red
Write-Host "  Stopping RAG Application Services" -ForegroundColor Red
Write-Host ("=" * 50) -ForegroundColor Red
Write-Host ""

# Stop all Python processes (Backend)
Write-Host "[1/3] Stopping Backend (Python)..." -ForegroundColor Yellow
try {
    # Check if python is running first to avoid error noise
    $pythonProc = Get-Process python -ErrorAction SilentlyContinue
    if ($pythonProc) {
        Stop-Process -Name python -Force -ErrorAction SilentlyContinue
        Write-Host "  [OK] Backend stopped successfully" -ForegroundColor Green
    } else {
        Write-Host "  [OK] No backend processes found" -ForegroundColor Gray
    }
}
catch {
    Write-Host "  [!] Error stopping backend: $_" -ForegroundColor Red
}

# Stop all Node processes (Frontend)
Write-Host "[2/3] Stopping Frontend (Node)..." -ForegroundColor Yellow
try {
    $nodeProc = Get-Process node -ErrorAction SilentlyContinue
    if ($nodeProc) {
        Stop-Process -Name node -Force -ErrorAction SilentlyContinue
        Write-Host "  [OK] Frontend stopped successfully" -ForegroundColor Green
    } else {
        Write-Host "  [OK] No frontend processes found" -ForegroundColor Gray
    }
}
catch {
    Write-Host "  [!] Error stopping frontend: $_" -ForegroundColor Red
}

# Verify ports are free
Write-Host "[3/3] Verifying ports are free..." -ForegroundColor Yellow
$port8000 = Get-NetTCPConnection -LocalPort 8000 -ErrorAction SilentlyContinue
$port5173 = Get-NetTCPConnection -LocalPort 5173 -ErrorAction SilentlyContinue

if ($port8000) {
    $p = $port8000.OwningProcess
    Write-Host "  [!] Port 8000 still in use (PID: $p)" -ForegroundColor Yellow
} else {
    Write-Host "  [OK] Port 8000 is free" -ForegroundColor Green
}

if ($port5173) {
    $p = $port5173.OwningProcess
    Write-Host "  [!] Port 5173 still in use (PID: $p)" -ForegroundColor Yellow
} else {
    Write-Host "  [OK] Port 5173 is free" -ForegroundColor Green
}

Write-Host ""
Write-Host ("=" * 50) -ForegroundColor Red
Write-Host "  All Services Stopped!" -ForegroundColor Red
Write-Host "  No API calls will be made to Groq" -ForegroundColor Red
Write-Host ("=" * 50) -ForegroundColor Red
Write-Host ""
