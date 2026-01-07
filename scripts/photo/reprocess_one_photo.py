#!/usr/bin/env python3
"""
Reprocess one photo to verify color processing works
"""
import os
import sys

# Add project root to path for imports
project_root = os.path.abspath(os.path.join(os.path.dirname(__file__), '..', '..'))
sys.path.insert(0, project_root)

from PIL import Image
from src.utils.image_processor import ImageProcessor

# Use the ACTUAL config
config_path = "config/config.json"
if os.path.exists(config_path):
    import json
    with open(config_path, 'r') as f:
        config = json.load(f)
    print(f"Loaded config from {config_path}")
else:
    print("ERROR: config/config.json not found!")
    exit(1)

print(f"Display type: {config['display'].get('type')}")
print(f"Color mode: {config['display'].get('color_mode')}")

# Create processor
processor = ImageProcessor(config)

# Find a JPG to process
photo_dir = "static/images/photos"
jpgs = [f for f in os.listdir(photo_dir) if f.lower().endswith(('.jpg', '.jpeg'))]

if not jpgs:
    print("No JPG files found!")
    exit(1)

# Process the first one
test_jpg = jpgs[0]
input_path = os.path.join(photo_dir, test_jpg)
output_path = os.path.join(photo_dir, "test_color_output.bmp")

print(f"\nProcessing {test_jpg}...")
print(f"Forcing mode='color'")

# Process with explicit color mode
result = processor.preprocess_image(input_path, output_path, mode='color')

if result:
    print(f"Saved to: {result}")
    
    # Check the result
    img = Image.open(result)
    print(f"\nResult check:")
    print(f"  Mode: {img.mode}")
    print(f"  Size: {img.size}")
    
    # Sample colors
    pixels = []
    for y in range(0, img.height, 50):
        for x in range(0, img.width, 50):
            pixels.append(img.getpixel((x, y)))
    
    unique = set(pixels)
    print(f"  Unique colors: {len(unique)}")
    if len(unique) <= 10:
        print(f"  Colors: {list(unique)}")
    
    # Check if it's grayscale
    if img.mode == 'RGB':
        is_grayscale = all(isinstance(p, tuple) and p[0] == p[1] == p[2] for p in unique)
        if is_grayscale:
            print("  WARNING: RGB mode but all colors are grayscale!")
        else:
            print("  SUCCESS: Image has actual colors!")
    elif img.mode == 'L':
        print("  ERROR: Image is in grayscale mode!")
else:
    print("Processing failed!")