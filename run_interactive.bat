@echo off
chcp 65001 >nul
echo ========================================
echo   Eslite Pet Books - Interactive Mode
echo ========================================

call venv\Scripts\activate.bat
python pet_books_interactive.py
