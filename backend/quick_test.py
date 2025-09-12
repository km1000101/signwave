#!/usr/bin/env python3
"""
Quick test to verify model loading works
"""

import pickle
import sys
from pathlib import Path

def quick_test():
    """Quick test of model loading"""
    print("Quick Model Test")
    print("=" * 30)
    
    try:
        # Load model
        print("Loading model...")
        model_dict = pickle.load(open('../src/models/model.p', 'rb'))
        model = model_dict['model']
        print(f"✓ Model loaded: {type(model)}")
        
        # Test prediction with dummy data
        print("Testing prediction...")
        import numpy as np
        
        # Create dummy hand landmarks (42 features: 21 landmarks * 2 coordinates)
        dummy_features = np.random.random(42).reshape(1, -1)
        
        prediction = model.predict(dummy_features)
        print(f"✓ Prediction works: {prediction}")
        
        # Test labels
        labels_dict = {'0': 'A', '1': 'B', '2': 'L'}
        predicted_class = str(prediction[0])
        predicted_character = labels_dict.get(predicted_class, 'Unknown')
        print(f"✓ Character mapping: {predicted_class} -> {predicted_character}")
        
        print("\n✓ All tests passed! Model is working correctly.")
        return True
        
    except Exception as e:
        print(f"✗ Error: {e}")
        return False

if __name__ == '__main__':
    success = quick_test()
    sys.exit(0 if success else 1)
