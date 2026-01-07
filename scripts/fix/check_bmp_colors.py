#!/usr/bin/env python3
"""
Check what colors are in the BMP file
"""
from PIL import Image

# Check the exact BMP that was selected
bmp_path = "static/images/photos/1420.bmp"

print(f"Checking {bmp_path}...")

img = Image.open(bmp_path)
print(f"Mode: {img.mode}")
print(f"Size: {img.size}")

# Get all unique colors
pixels = img.getdata()
unique_colors = set(pixels)

print(f"\nUnique colors in image: {len(unique_colors)}")
if len(unique_colors) <= 10:
    print("Colors found:")
    for color in sorted(unique_colors):
        print(f"  {color}")
else:
    print("Sample of colors:")
    for i, color in enumerate(sorted(unique_colors)[:10]):
        print(f"  {color}")

# Check if it's actually color or grayscale
if img.mode == 'RGB':
    # Check if all R,G,B values are equal (which would make it grayscale)
    is_grayscale = all(r == g == b for r, g, b in unique_colors)
    if is_grayscale:
        print("\nWARNING: Image is RGB mode but all colors are grayscale!")
    else:
        print("\nImage contains actual colors")
elif img.mode == 'L':
    print("\nWARNING: Image is in grayscale mode!")
elif img.mode == 'P':
    print("\nImage is in palette mode")
    print(f"Palette: {img.getpalette()[:21]}")  # First 7 colors