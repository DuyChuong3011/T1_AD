# Cleanup Script - Xóa files không cần thiết
# Chạy: .\cleanup.ps1

Write-Host "=" * 70 -ForegroundColor Cyan
Write-Host "🧹 CLEANING UP PROJECT" -ForegroundColor Cyan
Write-Host "=" * 70 -ForegroundColor Cyan

# 1. Virtual Environments
Write-Host "`n[1/6] Removing virtual environments..." -ForegroundColor Yellow

$venv_folders = @(".venv", ".venv312", "venv", "env")
foreach ($folder in $venv_folders) {
    if (Test-Path $folder) {
        Write-Host "  Removing $folder..." -ForegroundColor Gray
        Remove-Item -Path $folder -Recurse -Force -ErrorAction SilentlyContinue
        Write-Host "  ✅ $folder deleted" -ForegroundColor Green
    }
}

# 2. Python Cache
Write-Host "`n[2/6] Removing Python cache..." -ForegroundColor Yellow

Get-ChildItem -Path . -Recurse -Directory -Name "__pycache__" | ForEach-Object {
    $path = $_
    Write-Host "  Removing $path..." -ForegroundColor Gray
    Remove-Item -Path $path -Recurse -Force -ErrorAction SilentlyContinue
}
Write-Host "  ✅ __pycache__ cleaned" -ForegroundColor Green

# Remove .pyc files
Get-ChildItem -Path . -Recurse -Filter "*.pyc" | ForEach-Object {
    Remove-Item -Path $_.FullName -Force -ErrorAction SilentlyContinue
}
Write-Host "  ✅ .pyc files deleted" -ForegroundColor Green

# 3. Cache Directories
Write-Host "`n[3/6] Removing cache directories..." -ForegroundColor Yellow

$cache_dirs = @(".pytest_cache", ".mypy_cache", ".cache", "*.egg-info")
Get-ChildItem -Path . -Recurse -Directory -ErrorAction SilentlyContinue | Where-Object {
    $_.Name -match "(__pycache__|\.pytest_cache|\.mypy_cache|egg-info)"
} | ForEach-Object {
    Write-Host "  Removing $($_.Name)..." -ForegroundColor Gray
    Remove-Item -Path $_.FullName -Recurse -Force -ErrorAction SilentlyContinue
}
Write-Host "  ✅ Cache directories cleaned" -ForegroundColor Green

# 4. Raw Data (CSV files - keep processed)
Write-Host "`n[4/6] Removing raw data..." -ForegroundColor Yellow

if (Test-Path "data\raw") {
    Get-ChildItem -Path "data\raw" -Filter "*.csv" | ForEach-Object {
        Write-Host "  Removing $($_.Name)..." -ForegroundColor Gray
        Remove-Item -Path $_.FullName -Force -ErrorAction SilentlyContinue
    }
    Write-Host "  ✅ Raw CSV files deleted" -ForegroundColor Green
} else {
    Write-Host "  No data\raw folder found" -ForegroundColor Gray
}

# 5. Log Files & Temp
Write-Host "`n[5/6] Removing log files..." -ForegroundColor Yellow

Get-ChildItem -Path . -Recurse -Filter "*.log" -ErrorAction SilentlyContinue | ForEach-Object {
    Write-Host "  Removing $($_.Name)..." -ForegroundColor Gray
    Remove-Item -Path $_.FullName -Force -ErrorAction SilentlyContinue
}
Write-Host "  ✅ Log files deleted" -ForegroundColor Green

# 6. IDE Files (optional - keep if using these)
Write-Host "`n[6/6] Review IDE files..." -ForegroundColor Yellow

if (Test-Path ".vscode") {
    $size = (Get-ChildItem .vscode -Recurse | Measure-Object -Property Length -Sum).Sum / 1MB
    Write-Host "  .vscode folder: $([Math]::Round($size, 2)) MB" -ForegroundColor Gray
    Write-Host "  Keep? (Y/N): " -ForegroundColor Yellow -NoNewline
    $response = Read-Host
    if ($response -eq "Y" -or $response -eq "y") {
        Write-Host "  ✅ Keeping .vscode" -ForegroundColor Green
    } else {
        Remove-Item -Path ".vscode" -Recurse -Force
        Write-Host "  ✅ .vscode deleted" -ForegroundColor Green
    }
}

# Summary
Write-Host "`n" + "=" * 70 -ForegroundColor Cyan
Write-Host "📊 CLEANUP SUMMARY" -ForegroundColor Cyan
Write-Host "=" * 70 -ForegroundColor Cyan

# Calculate folder size
$folders = @(".", "src", "models", "data", "notebooks", "demo")
Write-Host "`nFolder Sizes:" -ForegroundColor White
foreach ($folder in $folders) {
    if (Test-Path $folder) {
        $size = (Get-ChildItem -Path $folder -Recurse -ErrorAction SilentlyContinue |
                 Measure-Object -Property Length -Sum).Sum / 1MB
        if ($size -gt 0) {
            Write-Host "  $folder`: $([Math]::Round($size, 2)) MB" -ForegroundColor Gray
        }
    }
}

# Total size
$total = (Get-ChildItem -Path . -Recurse -ErrorAction SilentlyContinue |
          Measure-Object -Property Length -Sum).Sum / 1MB
Write-Host "`n  TOTAL: $([Math]::Round($total, 2)) MB" -ForegroundColor Cyan

# What remains
Write-Host "`n✅ CLEANED UP:" -ForegroundColor Green
Write-Host "  ❌ .venv312 / venv / .venv" -ForegroundColor Green
Write-Host "  ❌ __pycache__" -ForegroundColor Green
Write-Host "  ❌ .pytest_cache" -ForegroundColor Green
Write-Host "  ❌ *.pyc files" -ForegroundColor Green
Write-Host "  ❌ data/raw/*.csv" -ForegroundColor Green

Write-Host "`n✅ KEPT:" -ForegroundColor Green
Write-Host "  ✅ src/" -ForegroundColor Green
Write-Host "  ✅ models/model.joblib" -ForegroundColor Green
Write-Host "  ✅ data/processed/" -ForegroundColor Green
Write-Host "  ✅ data/features/" -ForegroundColor Green
Write-Host "  ✅ notebooks/" -ForegroundColor Green
Write-Host "  ✅ demo/" -ForegroundColor Green

Write-Host "`n" + "=" * 70 -ForegroundColor Cyan
Write-Host "🚀 Ready for AWS Upload!" -ForegroundColor Cyan
Write-Host "=" * 70 -ForegroundColor Cyan

Write-Host "`nNext step:" -ForegroundColor Yellow
Write-Host "  aws s3 sync . s3://YOUR-BUCKET-NAME/code/ \" -ForegroundColor Gray
Write-Host "    --exclude '.git/*' --exclude '__pycache__/*'" -ForegroundColor Gray

Write-Host "`n" -ForegroundColor Cyan
