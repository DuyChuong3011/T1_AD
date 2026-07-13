# Installation Script - Install all dependencies
# Chạy: .\install.ps1

Write-Host "=" * 70 -ForegroundColor Cyan
Write-Host "📦 INSTALLING DEPENDENCIES" -ForegroundColor Cyan
Write-Host "=" * 70 -ForegroundColor Cyan

# Check Python
Write-Host "`n[1/4] Checking Python..." -ForegroundColor Yellow
$python = python --version
Write-Host "✅ Python: $python" -ForegroundColor Green

# Upgrade pip
Write-Host "`n[2/4] Upgrading pip..." -ForegroundColor Yellow
python -m pip install --upgrade pip --quiet
Write-Host "✅ pip upgraded" -ForegroundColor Green

# Install production dependencies
Write-Host "`n[3/4] Installing production dependencies..." -ForegroundColor Yellow
Write-Host "  (from requirements.txt)" -ForegroundColor Gray
pip install -r requirements.txt

if ($LASTEXITCODE -eq 0) {
    Write-Host "✅ Production dependencies installed" -ForegroundColor Green
} else {
    Write-Host "❌ Error installing production dependencies" -ForegroundColor Red
    exit 1
}

# Ask for dev dependencies
Write-Host "`n[4/4] Install development tools? (Y/N)" -ForegroundColor Yellow
$devInstall = Read-Host "Y/N"

if ($devInstall -eq "Y" -or $devInstall -eq "y") {
    Write-Host "Installing development dependencies..." -ForegroundColor Gray
    Write-Host "  (from requirements-dev.txt)" -ForegroundColor Gray
    pip install -r requirements-dev.txt

    if ($LASTEXITCODE -eq 0) {
        Write-Host "✅ Development dependencies installed" -ForegroundColor Green
    } else {
        Write-Host "⚠️  Some dev dependencies failed" -ForegroundColor Yellow
    }
} else {
    Write-Host "Skipped dev dependencies" -ForegroundColor Gray
}

# Verify installation
Write-Host "`n" + "=" * 70 -ForegroundColor Cyan
Write-Host "✅ VERIFICATION" -ForegroundColor Cyan
Write-Host "=" * 70 -ForegroundColor Cyan

$packages = @(
    "pandas",
    "numpy",
    "scikit-learn",
    "joblib",
    "boto3",
    "sagemaker",
    "fastapi",
    "uvicorn",
    "plotly"
)

Write-Host "`nKey packages installed:" -ForegroundColor White
foreach ($pkg in $packages) {
    try {
        $version = python -c "import $pkg; print($pkg.__version__)" 2>$null
        if ($LASTEXITCODE -eq 0) {
            Write-Host "  ✅ $pkg : $version" -ForegroundColor Green
        } else {
            Write-Host "  ❌ $pkg : NOT FOUND" -ForegroundColor Red
        }
    } catch {
        Write-Host "  ❌ $pkg : ERROR" -ForegroundColor Red
    }
}

# Summary
Write-Host "`n" + "=" * 70 -ForegroundColor Cyan
Write-Host "✅ INSTALLATION COMPLETE!" -ForegroundColor Cyan
Write-Host "=" * 70 -ForegroundColor Cyan

Write-Host "`nYou can now run:" -ForegroundColor Yellow
Write-Host "  python demo/quick_verify.py" -ForegroundColor Gray
Write-Host "  python demo/verify_with_raw_data.py" -ForegroundColor Gray
Write-Host "  uvicorn demo.api:app --port 8000" -ForegroundColor Gray
Write-Host "  python aws/processing_job.py --bucket ... --role ..." -ForegroundColor Gray

Write-Host "`n" -ForegroundColor Cyan
