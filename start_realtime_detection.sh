#!/bin/bash

echo "Starting Real-time Sign Language Detection System"
echo "================================================"

echo ""
echo "Checking Python installation..."
if ! command -v python3 &> /dev/null; then
    echo "ERROR: Python 3 is not installed or not in PATH"
    echo "Please install Python 3.7+ and try again"
    exit 1
fi

python3 --version

echo ""
echo "Installing backend dependencies..."
cd backend
pip3 install -r requirements.txt
if [ $? -ne 0 ]; then
    echo "ERROR: Failed to install dependencies"
    echo "Please check your internet connection and try again"
    exit 1
fi

echo ""
echo "Starting backend server..."
echo "The server will be available at: http://localhost:5000"
echo "Press Ctrl+C to stop the server"
echo ""
python3 app.py
