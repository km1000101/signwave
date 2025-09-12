@echo off
echo Starting Sign Language Detection System...
echo.

echo Checking if Python is installed...
python --version >nul 2>&1
if errorlevel 1 (
    echo ERROR: Python is not installed or not in PATH
    echo Please install Python from https://python.org
    pause
    exit /b 1
)

echo Python found!
echo.

echo Starting backend server...
echo The server will be available at: http://localhost:5000
echo Press Ctrl+C to stop the server
echo.

cd backend
python app.py

pause
