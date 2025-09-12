#!/usr/bin/env python3
"""
Integration test script for the real-time sign language detection system
"""

import requests
import json
import base64
import time
import sys
from pathlib import Path

# Test configuration
BACKEND_URL = 'http://localhost:5000'
TEST_IMAGE_PATH = 'test_image.jpg'  # You can create a simple test image

def test_backend_health():
    """Test if backend is running"""
    try:
        response = requests.get(f'{BACKEND_URL}/health', timeout=5)
        if response.status_code == 200:
            print("✓ Backend health check passed")
            return True
        else:
            print(f"✗ Backend health check failed: {response.status_code}")
            return False
    except requests.exceptions.RequestException as e:
        print(f"✗ Backend not reachable: {e}")
        return False

def test_backend_status():
    """Test backend status endpoint"""
    try:
        response = requests.get(f'{BACKEND_URL}/status', timeout=5)
        if response.status_code == 200:
            data = response.json()
            print(f"✓ Backend status: {data}")
            
            if data.get('model_loaded'):
                print("✓ Model is loaded")
            else:
                print("✗ Model is not loaded")
                
            if data.get('mediapipe_loaded'):
                print("✓ MediaPipe is loaded")
            else:
                print("✗ MediaPipe is not loaded")
                
            return data.get('model_loaded', False)
        else:
            print(f"✗ Status check failed: {response.status_code}")
            return False
    except requests.exceptions.RequestException as e:
        print(f"✗ Status check failed: {e}")
        return False

def create_test_image():
    """Create a simple test image"""
    try:
        from PIL import Image, ImageDraw
        import numpy as np
        
        # Create a simple test image
        img = Image.new('RGB', (640, 480), color='white')
        draw = ImageDraw.Draw(img)
        
        # Draw a simple hand-like shape
        draw.ellipse([200, 150, 400, 350], fill='lightblue', outline='blue')
        draw.ellipse([250, 200, 300, 250], fill='white')  # Palm
        draw.ellipse([280, 180, 290, 220], fill='white')  # Thumb
        
        # Save test image
        img.save(TEST_IMAGE_PATH)
        print(f"✓ Created test image: {TEST_IMAGE_PATH}")
        return True
    except ImportError:
        print("✗ PIL not available for creating test image")
        return False
    except Exception as e:
        print(f"✗ Failed to create test image: {e}")
        return False

def test_prediction():
    """Test prediction endpoint with a test image"""
    try:
        # Check if test image exists
        if not Path(TEST_IMAGE_PATH).exists():
            if not create_test_image():
                print("✗ Cannot create test image, skipping prediction test")
                return False
        
        # Read and encode test image
        with open(TEST_IMAGE_PATH, 'rb') as f:
            image_data = base64.b64encode(f.read()).decode('utf-8')
        
        # Send prediction request
        response = requests.post(f'{BACKEND_URL}/predict', 
                               json={'image': image_data},
                               timeout=10)
        
        if response.status_code == 200:
            data = response.json()
            print(f"✓ Prediction test passed: {data}")
            return True
        else:
            print(f"✗ Prediction test failed: {response.status_code}")
            print(f"Response: {response.text}")
            return False
            
    except requests.exceptions.RequestException as e:
        print(f"✗ Prediction test failed: {e}")
        return False
    except Exception as e:
        print(f"✗ Prediction test error: {e}")
        return False

def test_model_files():
    """Test if model files exist"""
    model_path = Path('../src/models/model.p')
    data_path = Path('../src/models/data.pickle')
    
    if model_path.exists():
        print("✓ Model file (model.p) found")
    else:
        print("✗ Model file (model.p) not found")
        return False
    
    if data_path.exists():
        print("✓ Data file (data.pickle) found")
    else:
        print("✗ Data file (data.pickle) not found")
        return False
    
    return True

def cleanup():
    """Clean up test files"""
    try:
        if Path(TEST_IMAGE_PATH).exists():
            Path(TEST_IMAGE_PATH).unlink()
            print("✓ Cleaned up test files")
    except Exception as e:
        print(f"✗ Cleanup error: {e}")

def main():
    """Run all integration tests"""
    print("Real-time Sign Language Detection - Integration Test")
    print("=" * 60)
    
    tests_passed = 0
    total_tests = 5
    
    # Test 1: Model files
    print("\n1. Testing model files...")
    if test_model_files():
        tests_passed += 1
    
    # Test 2: Backend health
    print("\n2. Testing backend health...")
    if test_backend_health():
        tests_passed += 1
    
    # Test 3: Backend status
    print("\n3. Testing backend status...")
    if test_backend_status():
        tests_passed += 1
    
    # Test 4: Prediction endpoint
    print("\n4. Testing prediction endpoint...")
    if test_prediction():
        tests_passed += 1
    
    # Test 5: Frontend accessibility (basic check)
    print("\n5. Testing frontend accessibility...")
    frontend_path = Path('../src/pages/realtime.html')
    if frontend_path.exists():
        print("✓ Frontend page found")
        tests_passed += 1
    else:
        print("✗ Frontend page not found")
    
    # Summary
    print("\n" + "=" * 60)
    print(f"Integration Test Results: {tests_passed}/{total_tests} tests passed")
    
    if tests_passed == total_tests:
        print("✓ All tests passed! The system is ready to use.")
        print("\nTo start using the system:")
        print("1. Start the backend: cd backend && python app.py")
        print("2. Open src/pages/realtime.html in your browser")
        print("3. Allow camera access and start detecting signs!")
    else:
        print("✗ Some tests failed. Please check the issues above.")
        print("\nTroubleshooting:")
        print("- Ensure backend dependencies are installed: pip install -r requirements.txt")
        print("- Check if model files exist in src/models/")
        print("- Verify backend server is running on localhost:5000")
    
    # Cleanup
    cleanup()
    
    return tests_passed == total_tests

if __name__ == '__main__':
    success = main()
    sys.exit(0 if success else 1)
