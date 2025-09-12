#!/bin/bash

echo "Starting Sign Language Detection System..."
echo

echo "Checking if Python is installed..."
if ! command -v python3 &> /dev/null; then
    echo "ERROR: Python3 is not installed"
    echo "Please install Python3 from your package manager"
    exit 1
fi

echo "Python found!"
echo

echo "Starting backend server..."
echo "The server will be available at: http://localhost:5000"
echo "Press Ctrl+C to stop the server"
echo

cd backend
python3 app.py
