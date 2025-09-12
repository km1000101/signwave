@echo off
echo Starting Real-time Sign Language Detection System
echo ================================================

echo.
echo Checking Python installation...
python --version
if %errorlevel% neq 0 (
    echo ERROR: Python is not installed or not in PATH
    echo Please install Python 3.7+ and try again
    pause
    exit /b 1
)

echo.
echo Installing backend dependencies...
cd backend
pip install -r requirements.txt
if %errorlevel% neq 0 (
    echo ERROR: Failed to install dependencies
    echo Please check your internet connection and try again
    pause
    exit /b 1
)

echo.
echo Starting backend server...
echo The server will be available at: http://localhost:5000
echo Press Ctrl+C to stop the server
echo.
python app.py

pause
