#!/usr/bin/env python3
"""
Process photos from uploads directory to create color BMPs
"""
import os
import json
from src.utils.image_processor import ImageProcessor
from PIL import Image

print("=== Processing Uploads to Color BMPs ===\n")

# Load config
config_path = "config/config.json"
with open(config_path, 'r') as f:
    config = json.load(f)

print(f"Config: {config['display']['type']} in {config['display']['color_mode']} mode\n")

# Force color mode in config
config['display']['color_mode'] = 'color'

# Create processor
processor = ImageProcessor(config)

uploads_dir = "static/images/photos/uploads"
photo_dir = "static/images/photos"

if not os.path.exists(uploads_dir):
    print(f"ERROR: {uploads_dir} not found!")
    exit(1)

# Get all image files from uploads
image_extensions = ('.jpg', '.jpeg', '.png', '.gif', '.bmp', '.heic', '.heif')
uploads = [f for f in os.listdir(uploads_dir) if f.lower().endswith(image_extensions)]

print(f"Found {len(uploads)} images in uploads directory\n")

if not uploads:
    print("No images found in uploads directory!")
    exit(1)

# First, delete old grayscale BMPs
old_bmps = [f for f in os.listdir(photo_dir) if f.lower().endswith('.bmp')]
print(f"Deleting {len(old_bmps)} old grayscale BMPs...")
for bmp in old_bmps:
    bmp_path = os.path.join(photo_dir, bmp)
    if os.path.isfile(bmp_path):  # Make sure it's a file, not directory
        os.remove(bmp_path)
        print(f"  Deleted: {bmp}")

print(f"\nProcessing {len(uploads)} images from uploads...\n")

# Process each upload
for i, filename in enumerate(uploads, 1):
    input_path = os.path.join(uploads_dir, filename)
    
    # Create output filename
    base_name = os.path.splitext(filename)[0]
    output_filename = f"{base_name}.bmp"
    output_path = os.path.join(photo_dir, output_filename)
    
    print(f"[{i}/{len(uploads)}] Processing {filename}...")
    
    try:
        # Force color mode
        result = processor.preprocess_image(input_path, output_path, mode='color')
        
        if result:
            # Verify it's actually color
            img = Image.open(result)
            
            # Quick color check
            if img.mode == 'RGB':
                pixels = list(img.getdata())[::5000]  # Sample pixels
                has_color = any(p[0] != p[1] or p[1] != p[2] for p in pixels if isinstance(p, tuple))
                
                if has_color:
                    print(f"  ✓ Created COLOR: {output_filename}")
                else:
                    print(f"  ⚠ Created but appears grayscale: {output_filename}")
            else:
                print(f"  ✗ ERROR: Created in {img.mode} mode: {output_filename}")
        else:
            print(f"  ✗ Failed to process")
            
    except Exception as e:
        print(f"  ✗ Error: {e}")

print("\nDone! Now restart the display service:")
print("  sudo systemctl restart inkframe-display.service")