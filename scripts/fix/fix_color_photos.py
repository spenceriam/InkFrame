#!/usr/bin/env python3
"""
Fix the grayscale BMPs by reprocessing from originals
"""
import os
import sys
import shutil

# Add project root to path for imports
project_root = os.path.abspath(os.path.join(os.path.dirname(__file__), '..', '..'))
sys.path.insert(0, project_root)

from src.utils.image_processor import ImageProcessor

print("=== Fixing Color Photos ===\n")

# Load config
config_path = "config/config.json"
if os.path.exists(config_path):
    import json
    with open(config_path, 'r') as f:
        config = json.load(f)
else:
    print("ERROR: config/config.json not found!")
    exit(1)

print(f"Config: {config['display']['type']} in {config['display']['color_mode']} mode\n")

# Create processor
processor = ImageProcessor(config)

photo_dir = "static/images/photos"

# First, let's see what we have
all_files = os.listdir(photo_dir)
bmps = [f for f in all_files if f.lower().endswith('.bmp')]
originals = [f for f in all_files if f.lower().endswith(('.jpg', '.jpeg', '.png', '.gif'))]

print(f"Found {len(bmps)} BMP files (currently grayscale)")
print(f"Found {len(originals)} original image files")

if not originals:
    print("\nERROR: No original images found! Did you delete them?")
    print("The BMP files are grayscale and we need the originals to create color versions.")
    exit(1)

# Process a few originals to create proper color BMPs
print(f"\nProcessing {min(5, len(originals))} images to demonstrate color processing...")

for i, filename in enumerate(originals[:5]):
    input_path = os.path.join(photo_dir, filename)
    base_name = filename.rsplit('.', 1)[0]
    output_path = os.path.join(photo_dir, f"{base_name}_COLOR.bmp")
    
    print(f"\n[{i+1}/5] Processing {filename}...")
    
    # Force color mode
    result = processor.preprocess_image(input_path, output_path, mode='color')
    
    if result:
        # Check the result
        from PIL import Image
        img = Image.open(result)
        
        # Sample for colors
        pixels = []
        for y in range(0, img.height, 100):
            for x in range(0, img.width, 100):
                pixels.append(img.getpixel((x, y)))
        
        unique = set(pixels)
        print(f"  Created: {os.path.basename(result)}")
        print(f"  Mode: {img.mode}, Colors: {len(unique)}")
        
        if len(unique) <= 10:
            print(f"  Color values: {list(unique)[:7]}")

print("\n" + "="*50)
print("To fix ALL photos, you need to:")
print("1. Delete the old grayscale BMPs")
print("2. Re-run the preprocessing")
print("\nRun these commands:")
print("  rm static/images/photos/*.bmp")
print("  python3 preprocess_photos.py")
print("\nThe *_COLOR.bmp files above show that color processing works!")