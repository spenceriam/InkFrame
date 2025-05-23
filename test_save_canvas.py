#!/usr/bin/env python3
"""
Save what the photo manager is trying to display
"""
import logging
from PIL import Image
from src.display.photo_manager import PhotoManager

logging.basicConfig(level=logging.INFO)

# Monkey patch the display method to save the image
original_display = None

def save_display_image(self, image, force_refresh=False):
    """Save the image instead of displaying it"""
    print(f"Saving image that would be displayed: {image.size}, mode={image.mode}")
    image.save("canvas_to_display.png")
    image.save("canvas_to_display.bmp")
    
    # Count colors
    pixels = list(image.getdata())
    unique_colors = set(pixels)
    print(f"Unique colors in final canvas: {len(unique_colors)}")
    if len(unique_colors) <= 10:
        print(f"Colors: {unique_colors}")
    
    return True

print("Patching display to save image...")

# Create photo manager
pm = PhotoManager()

# Patch the display method
pm.display.display_image_buffer = lambda img, force: save_display_image(pm.display, img, force)

# Try to display
print("\nCalling display_photo...")
result = pm.display_photo(force_refresh=True)

print(f"\nResult: {result}")
print("Check canvas_to_display.png to see what would be displayed")