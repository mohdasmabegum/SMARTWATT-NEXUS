@echo off
REM SMARTWATT NEXUS - Startup Script for Windows

echo.
echo ========================================
echo   SMARTWATT NEXUS - Startup
echo ========================================
echo.

REM Check if Python is installed
python --version >nul 2>&1
if errorlevel 1 (
    echo Error: Python is not installed or not in PATH
    echo Please install Python 3.8+ from https://www.python.org
    pause
    exit /b 1
)

echo [1/5] Checking Python version...
python --version

REM Create virtual environment if it doesn't exist
if not exist venv (
    echo [2/5] Creating virtual environment...
    python -m venv venv
) else (
    echo [2/5] Virtual environment already exists
)

REM Activate virtual environment
echo [3/5] Activating virtual environment...
call venv\Scripts\activate.bat

REM Install requirements (set LIGHT=1 to use lightweight requirements)
echo [4/5] Installing dependencies...
if "%LIGHT%"=="1" (
    echo Using lightweight requirements (requirements-light.txt)
    pip install -q -r requirements-light.txt
) else (
    pip install -q -r requirements.txt
)

REM Initialize database with sample data
echo [5/5] Initializing database...
cd backend
python init_data.py

REM Run Flask application
echo.
echo ========================================
echo   Starting SMARTWATT NEXUS...
echo ========================================
echo.
echo Flask app starting at: http://localhost:5000
echo.
echo Test Credentials:
echo   Username: demo_user
echo   Password: password123
echo.
echo Press Ctrl+C to stop the server
echo.

python app.py

pause
