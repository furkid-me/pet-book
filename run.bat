@echo off
chcp 65001 >nul
echo ========================================
echo   Eslite Pet Books Scraper - Running
echo ========================================
echo.

call venv\Scripts\activate.bat
python pet_books_scraper.py

echo.
echo ========================================
echo   Done! Check the Excel and CSV files
echo ========================================
pause
