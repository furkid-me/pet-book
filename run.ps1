# Eslite Pet Books Scraper - Run Script
Write-Host "========================================" -ForegroundColor Cyan
Write-Host "  Eslite Pet Books Scraper - Running" -ForegroundColor Cyan
Write-Host "========================================" -ForegroundColor Cyan
Write-Host ""

# Activate venv
if (-not (Test-Path "venv\Scripts\Activate.ps1")) {
    Write-Host "ERROR: Please run setup.ps1 first!" -ForegroundColor Red
    pause
    exit 1
}

& ".\venv\Scripts\Activate.ps1"

# Run scraper
Write-Host "Starting scraper..." -ForegroundColor Yellow
Write-Host ""
python pet_books_scraper.py

Write-Host ""
Write-Host "========================================" -ForegroundColor Green
Write-Host "  Done! Check the Excel and CSV files" -ForegroundColor Green
Write-Host "========================================" -ForegroundColor Green
pause
