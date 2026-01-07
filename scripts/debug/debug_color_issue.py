#!/usr/bin/env python3
"""
Debug why colors aren't showing
"""
import os
from PIL import Image

print("=== Debugging Color Issue ===\n")

# 1. Check if BMP files were created
photo_dir = "static/images/photos"
bmps = [f for f in os.listdir(photo_dir) if f.lower().endswith('.bmp')]
print(f"BMP files found: {len(bmps)}")
if bmps:
    print(f"First few: {bmps[:3]}")

# 2. Check a BMP file's colors
if bmps:
    test_bmp = os.path.join(photo_dir, bmps[0])
    print(f"\nChecking {test_bmp}:")
    
    img = Image.open(test_bmp)
    print(f"  Mode: {img.mode}")
    print(f"  Size: {img.size}")
    
    # Sample some pixels
    pixels = []
    for y in range(0, img.height, 50):
        for x in range(0, img.width, 50):
            pixels.append(img.getpixel((x, y)))
    
    unique_colors = set(pixels)
    print(f"  Unique colors sampled: {len(unique_colors)}")
    print(f"  Colors: {list(unique_colors)[:10]}")
    
    # Expected 7 colors
    expected = [
        (0, 0, 0),      # Black
        (255, 255, 255), # White
        (0, 255, 0),    # Green
        (0, 0, 255),    # Blue
        (255, 0, 0),    # Red
        (255, 255, 0),  # Yellow
        (255, 128, 0)   # Orange
    ]
    
    # Check if colors match expected
    found_colors = []
    for color in expected:
        if color in unique_colors:
            found_colors.append(color)
    
    print(f"\nExpected colors found: {len(found_colors)}/7")
    print(f"Found: {found_colors}")

# 3. Test direct display of color image
print("\n=== Testing Direct Color Display ===")

# Create a simple color test image
test_img = Image.new('RGB', (800, 480), (255, 255, 255))
pixels = test_img.load()

# Draw color bars
colors = [
    (0, 0, 0),      # Black
    (255, 0, 0),    # Red
    (0, 255, 0),    # Green
    (0, 0, 255),    # Blue
    (255, 255, 0),  # Yellow
    (255, 128, 0),  # Orange
    (255, 255, 255) # White
]

bar_width = 800 // len(colors)
for i, color in enumerate(colors):
    x_start = i * bar_width
    x_end = (i + 1) * bar_width
    for x in range(x_start, x_end):
        for y in range(480):
            pixels[x, y] = color

# Save test image
test_img.save("color_bars_test.bmp")
print("Created color_bars_test.bmp")

# 4. Check what the photo manager would select
print("\n=== Photo Manager Check ===")
all_photos = [f for f in os.listdir(photo_dir) if f.lower().endswith(('.jpg', '.jpeg', '.png', '.bmp'))]
print(f"Total photos (all formats): {len(all_photos)}")
print(f"File types: {set(f.split('.')[-1].lower() for f in all_photos)}")

# Check if photo manager prefers BMP
if bmps and any(f.endswith('.jpg') for f in all_photos):
    print("\nWARNING: Both BMP and JPG files exist!")
    print("Photo manager might be selecting JPG files instead of BMP")