#!/usr/bin/env python3
"""
Preprocess all photos for color display
"""
import os
import sys

# Add project root to path for imports
project_root = os.path.abspath(os.path.join(os.path.dirname(__file__), '..', '..'))
sys.path.insert(0, project_root)

from src.utils.image_processor import ImageProcessor

print("Preprocessing photos for 7-color display...")

config = {
    'display': {
        'type': '7in3f', 
        'color_mode': 'color', 
        'enable_dithering': True,
        'contrast_factor': 1.2,
        'brightness_factor': 1.1
    },
    'photos': {
        'directory': 'static/images/photos', 
        'max_width': 800, 
        'max_height': 440, 
        'format': 'bmp'
    }
}

processor = ImageProcessor(config)
photo_dir = 'static/images/photos'

# Count photos
photos = [f for f in os.listdir(photo_dir) if f.lower().endswith(('.jpg', '.jpeg', '.png'))]
print(f"Found {len(photos)} photos to process")

# Process each photo
for i, f in enumerate(photos, 1):
    input_path = os.path.join(photo_dir, f)
    print(f"[{i}/{len(photos)}] Processing {f}...")
    
    try:
        result = processor.preprocess_image(input_path, mode='color')
        if result:
            print(f"  ✓ Created: {os.path.basename(result)}")
        else:
            print(f"  ✗ Failed to process")
    except Exception as e:
        print(f"  ✗ Error: {e}")

print("\nDone! Processed photos are saved as .bmp files with 7-color quantization")