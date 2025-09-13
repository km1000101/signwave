#!/usr/bin/env python3
"""
Test script for ISL_NEW model integration
This script tests the backend integration with the ISL_NEW model
"""

import requests
import json
import time
import sys
import os

# Backend URL
BACKEND_URL = 'http://localhost:5000'

def test_backend_status():
    """Test if the backend is running and check model status"""
    print("🔍 Testing backend status...")
    
    try:
        response = requests.get(f"{BACKEND_URL}/status", timeout=5)
        if response.status_code == 200:
            data = response.json()
            print("✅ Backend is running")
            print(f"   - Model loaded: {data.get('model_loaded', False)}")
            print(f"   - ISL_NEW model loaded: {data.get('isl_new_model_loaded', False)}")
            print(f"   - MediaPipe loaded: {data.get('mediapipe_loaded', False)}")
            print(f"   - Supported labels: {data.get('supported_labels', [])}")
            print(f"   - ISL_NEW supported labels: {data.get('isl_new_supported_labels', [])}")
            return data.get('isl_new_model_loaded', False)
        else:
            print(f"❌ Backend returned status code: {response.status_code}")
            return False
    except requests.exceptions.RequestException as e:
        print(f"❌ Cannot connect to backend: {e}")
        print("   Make sure to start the backend server with: python backend/app.py")
        return False

def test_isl_new_prediction():
    """Test ISL_NEW model prediction with sample features"""
    print("\n🧪 Testing ISL_NEW prediction...")
    
    # Sample hand features (84 features as expected by ISL_NEW model)
    sample_features = [0.1] * 84  # Dummy features for testing
    
    try:
        response = requests.post(
            f"{BACKEND_URL}/isl_new_predict",
            json={'features': sample_features},
            timeout=10
        )
        
        if response.status_code == 200:
            data = response.json()
            print("✅ ISL_NEW prediction successful")
            print(f"   - Prediction: {data.get('prediction', 'N/A')}")
            print(f"   - Confidence: {data.get('confidence', 0):.2f}")
            print(f"   - Model: {data.get('model', 'N/A')}")
            print(f"   - Success: {data.get('success', False)}")
            return True
        else:
            print(f"❌ ISL_NEW prediction failed with status: {response.status_code}")
            print(f"   Response: {response.text}")
            return False
    except requests.exceptions.RequestException as e:
        print(f"❌ ISL_NEW prediction request failed: {e}")
        return False

def test_health_endpoint():
    """Test the health endpoint"""
    print("\n🏥 Testing health endpoint...")
    
    try:
        response = requests.get(f"{BACKEND_URL}/health", timeout=5)
        if response.status_code == 200:
            data = response.json()
            print("✅ Health check passed")
            print(f"   - Status: {data.get('status', 'N/A')}")
            return True
        else:
            print(f"❌ Health check failed with status: {response.status_code}")
            return False
    except requests.exceptions.RequestException as e:
        print(f"❌ Health check request failed: {e}")
        return False

def check_isl_new_files():
    """Check if ISL_NEW model files exist"""
    print("\n📁 Checking ISL_NEW model files...")
    
    model_paths = [
        'ISL_NEW/model.p',
        'ISL_NEW/data.pickle'
    ]
    
    all_exist = True
    for path in model_paths:
        if os.path.exists(path):
            size = os.path.getsize(path)
            print(f"✅ {path} exists ({size:,} bytes)")
        else:
            print(f"❌ {path} not found")
            all_exist = False
    
    return all_exist

def main():
    """Main test function"""
    print("🚀 ISL_NEW Integration Test")
    print("=" * 50)
    
    # Check if model files exist
    files_exist = check_isl_new_files()
    
    # Test backend status
    backend_running = test_backend_status()
    
    # Test health endpoint
    health_ok = test_health_endpoint()
    
    # Test ISL_NEW prediction if backend is running
    prediction_ok = False
    if backend_running:
        prediction_ok = test_isl_new_prediction()
    
    # Summary
    print("\n📊 Test Summary")
    print("=" * 50)
    print(f"Model files exist: {'✅' if files_exist else '❌'}")
    print(f"Backend running: {'✅' if backend_running else '❌'}")
    print(f"Health check: {'✅' if health_ok else '❌'}")
    print(f"ISL_NEW prediction: {'✅' if prediction_ok else '❌'}")
    
    if files_exist and backend_running and health_ok and prediction_ok:
        print("\n🎉 All tests passed! ISL_NEW integration is working correctly.")
        return 0
    else:
        print("\n⚠️  Some tests failed. Please check the issues above.")
        return 1

if __name__ == "__main__":
    sys.exit(main())
