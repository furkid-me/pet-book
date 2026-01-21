@echo off
chcp 65001 >nul
echo ========================================
echo   Eslite Pet Books Scraper - Setup
echo ========================================
echo.

echo Creating virtual environment...
python -m venv venv

echo.
echo Installing packages...
call venv\Scripts\activate.bat
pip install -r requirements.txt

echo.
echo Installing Playwright browser...
playwright install chromium

echo.
echo ========================================
echo   Setup complete!
echo   Run 'run.bat' to start scraping
echo ========================================
pause
