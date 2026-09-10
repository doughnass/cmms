@echo off
REM Start Django Development Server for CMMS Project
REM Usage: Double-click this file or run in CMD

echo ========================================
echo Starting CMMS Django Server
echo ========================================
echo.

cd /d "%~dp0"

REM Check if virtual environment exists
if not exist ".venv\Scripts\python.exe" (
    echo ERROR: Virtual environment not found!
    echo Please create venv first: python -m venv .venv
    pause
    exit /b 1
)

echo Activating virtual environment...
call .venv\Scripts\activate.bat

echo.
echo Starting Django server at http://127.0.0.1:8000/
echo Press CTRL+C to stop the server
echo ========================================
echo.

REM Run Django server
python manage.py runserver

pause
