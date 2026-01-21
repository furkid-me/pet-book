# Eslite Pet Books Scraper - Setup Script
Write-Host "========================================" -ForegroundColor Cyan
Write-Host "  Eslite Pet Books Scraper - Setup" -ForegroundColor Cyan
Write-Host "========================================" -ForegroundColor Cyan
Write-Host ""

# Check Python
Write-Host "Checking Python..." -ForegroundColor Yellow
$pythonCmd = Get-Command python -ErrorAction SilentlyContinue
if (-not $pythonCmd) {
    Write-Host "ERROR: Python not found! Please install Python first." -ForegroundColor Red
    Write-Host "Download from: https://www.python.org/downloads/" -ForegroundColor Red
    pause
    exit 1
}

python --version

# Create venv
Write-Host ""
Write-Host "Creating virtual environment..." -ForegroundColor Yellow
python -m venv venv

if (-not (Test-Path "venv\Scripts\activate.ps1")) {
    Write-Host "ERROR: Failed to create virtual environment" -ForegroundColor Red
    pause
    exit 1
}

# Activate and install
Write-Host ""
Write-Host "Installing packages..." -ForegroundColor Yellow
& ".\venv\Scripts\Activate.ps1"
pip install playwright pandas openpyxl

Write-Host ""
Write-Host "Installing Playwright browser (this may take a few minutes)..." -ForegroundColor Yellow
playwright install chromium

Write-Host ""
Write-Host "========================================" -ForegroundColor Green
Write-Host "  Setup complete!" -ForegroundColor Green
Write-Host "  Run: .\run.ps1" -ForegroundColor Green
Write-Host "========================================" -ForegroundColor Green
pause
