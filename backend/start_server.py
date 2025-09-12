#!/usr/bin/env python3
"""
Startup script for the Sign Language Detection Backend Server
"""

import os
import sys
import subprocess
import time
import webbrowser
from pathlib import Path

def check_dependencies():
    """Check if required dependencies are installed"""
    try:
        import flask
        import cv2
        import mediapipe
        import numpy
        import PIL
        import sklearn
        print("✓ All dependencies are installed")
        return True
    except ImportError as e:
        print(f"✗ Missing dependency: {e}")
        print("Please install dependencies with: pip install -r requirements.txt")
        return False

def check_model_files():
    """Check if model files exist"""
    model_path = Path("../src/models/model.p")
    if model_path.exists():
        print("✓ Model file found")
        return True
    else:
        print("✗ Model file not found at ../src/models/model.p")
        return False

def start_server():
    """Start the Flask server"""
    print("Starting Sign Language Detection Backend Server...")
    print("Server will be available at: http://localhost:5000")
    print("Press Ctrl+C to stop the server")
    print("-" * 50)
    
    try:
        # Change to backend directory
        os.chdir(Path(__file__).parent)
        
        # Start the Flask app
        subprocess.run([sys.executable, "app.py"])
        
    except KeyboardInterrupt:
        print("\nServer stopped by user")
    except Exception as e:
        print(f"Error starting server: {e}")

def main():
    """Main function"""
    print("Sign Language Detection Backend Server")
    print("=" * 40)
    
    # Check dependencies
    if not check_dependencies():
        return
    
    # Check model files
    if not check_model_files():
        return
    
    # Start server
    start_server()

if __name__ == "__main__":
    main()
