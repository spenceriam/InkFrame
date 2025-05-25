#!/usr/bin/env python3
"""
Check what's left in the photos directory
"""
import os
from PIL import Image

photo_dir = "static/images/photos"

print(f"Contents of {photo_dir}:\n")

files = os.listdir(photo_dir)
files.sort()

for f in files:
    filepath = os.path.join(photo_dir, f)
    size = os.path.getsize(filepath)
    
    # Check if it's an image
    if f.lower().endswith(('.bmp', '.jpg', '.jpeg', '.png', '.gif')):
        try:
            img = Image.open(filepath)
            print(f"{f:<30} {size:>10} bytes   {img.mode} {img.size}")
        except:
            print(f"{f:<30} {size:>10} bytes   [can't read]")
    else:
        print(f"{f:<30} {size:>10} bytes")

print(f"\nTotal files: {len(files)}")

# Check if any are color
print("\nChecking for color images...")
for f in files:
    if f.lower().endswith('.bmp'):
        filepath = os.path.join(photo_dir, f)
        img = Image.open(filepath)
        if img.mode == 'RGB':
            # Check if it's actually color or just RGB grayscale
            pixels = img.getdata()
            sample = list(pixels)[::1000]  # Sample every 1000th pixel
            has_color = any(p[0] != p[1] or p[1] != p[2] for p in sample if isinstance(p, tuple))
            if has_color:
                print(f"  {f} - Has actual colors!")
            else:
                print(f"  {f} - RGB mode but grayscale values")
        else:
            print(f"  {f} - Mode: {img.mode}")