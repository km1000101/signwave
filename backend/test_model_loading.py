#!/usr/bin/env python3
"""
Test script to verify model loading works correctly
"""

import pickle
import sys
from pathlib import Path

def test_model_loading():
    """Test loading the model.p file"""
    print("Testing model loading...")
    
    # Try different possible paths for the model
    model_paths = [
        'src/models/model.p',
        '../src/models/model.p',
        '../../src/models/model.p',
        './src/models/model.p'
    ]
    
    for model_path in model_paths:
        try:
            print(f"Trying to load model from: {model_path}")
            
            # Check if file exists
            if not Path(model_path).exists():
                print(f"  File not found at: {model_path}")
                continue
            
            print(f"  File exists, attempting to load...")
            
            # Try to load the model
            with open(model_path, 'rb') as f:
                model_dict = pickle.load(f)
            
            print(f"  Successfully loaded pickle file!")
            print(f"  Keys in model_dict: {list(model_dict.keys())}")
            
            # Check if 'model' key exists
            if 'model' in model_dict:
                model = model_dict['model']
                print(f"  Model loaded successfully!")
                print(f"  Model type: {type(model)}")
                
                # Try to get some basic info about the model
                if hasattr(model, 'predict'):
                    print(f"  Model has predict method")
                if hasattr(model, 'classes_'):
                    print(f"  Model classes: {model.classes_}")
                if hasattr(model, 'feature_importances_'):
                    print(f"  Model has feature importances")
                
                return True
            else:
                print(f"  Error: 'model' key not found in pickle file")
                print(f"  Available keys: {list(model_dict.keys())}")
                
        except Exception as e:
            print(f"  Error loading model from {model_path}: {e}")
            continue
    
    print("Failed to load model from any path")
    return False

def test_data_pickle():
    """Test loading the data.pickle file"""
    print("\nTesting data.pickle loading...")
    
    data_paths = [
        'src/models/data.pickle',
        '../src/models/data.pickle',
        '../../src/models/data.pickle',
        './src/models/data.pickle'
    ]
    
    for data_path in data_paths:
        try:
            print(f"Trying to load data from: {data_path}")
            
            if not Path(data_path).exists():
                print(f"  File not found at: {data_path}")
                continue
            
            print(f"  File exists, attempting to load...")
            
            with open(data_path, 'rb') as f:
                data = pickle.load(f)
            
            print(f"  Successfully loaded data.pickle!")
            print(f"  Data type: {type(data)}")
            
            if isinstance(data, dict):
                print(f"  Data keys: {list(data.keys())}")
            elif isinstance(data, list):
                print(f"  Data length: {len(data)}")
            elif hasattr(data, 'shape'):
                print(f"  Data shape: {data.shape}")
            
            return True
            
        except Exception as e:
            print(f"  Error loading data from {data_path}: {e}")
            continue
    
    print("Failed to load data.pickle from any path")
    return False

def main():
    """Main test function"""
    print("Model Loading Test")
    print("=" * 40)
    
    # Test current working directory
    print(f"Current working directory: {Path.cwd()}")
    
    # Test model loading
    model_loaded = test_model_loading()
    
    # Test data loading
    data_loaded = test_data_pickle()
    
    print("\n" + "=" * 40)
    print("Test Results:")
    print(f"Model loaded: {'✓' if model_loaded else '✗'}")
    print(f"Data loaded: {'✓' if data_loaded else '✗'}")
    
    if model_loaded and data_loaded:
        print("\n✓ All tests passed! Model files are working correctly.")
        return True
    else:
        print("\n✗ Some tests failed. Check the errors above.")
        return False

if __name__ == '__main__':
    success = main()
    sys.exit(0 if success else 1)
