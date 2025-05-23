#!/usr/bin/env python3
"""
Test the complete color processing pipeline
"""
import os
from PIL import Image, ImageOps
from src.utils.image_processor import ImageProcessor
from src.display.photo_manager import PhotoManager

# Test 1: Check image processor output
print("=== Testing Image Processor ===")
config = {
    "display": {
        "type": "7in3f",
        "color_mode": "color",
        "enable_dithering": True
    },
    "photos": {
        "directory": "static/images/photos",
        "max_width": 800,
        "max_height": 440,
        "format": "bmp"
    }
}

processor = ImageProcessor(config)
photos = [f for f in os.listdir("static/images/photos") if f.lower().endswith(('.jpg', '.jpeg', '.png', '.bmp'))]

if photos:
    test_photo = os.path.join("static/images/photos", photos[0])
    print(f"Processing: {test_photo}")
    
    # Process for color
    output = processor.preprocess_image(test_photo, "test_color_processed.bmp", mode="color")
    
    if output:
        img = Image.open(output)
        print(f"Processed image: {img.size}, mode={img.mode}")
        
        # Check colors
        pixels = list(img.getdata())
        unique_colors = set(pixels)
        print(f"Unique colors after processing: {len(unique_colors)}")
        if len(unique_colors) <= 10:
            print(f"Colors: {unique_colors}")

# Test 2: Check what happens with ImageOps.invert
print("\n=== Testing ImageOps.invert ===")
if output:
    img = Image.open(output)
    print(f"Before invert: mode={img.mode}")
    
    inverted = ImageOps.invert(img)
    print(f"After invert: mode={inverted.mode}")
    
    # Check if colors are preserved
    pixels = list(inverted.getdata())
    unique_colors = set(pixels)
    print(f"Unique colors after invert: {len(unique_colors)}")
    if len(unique_colors) <= 10:
        print(f"Colors: {unique_colors}")
    
    inverted.save("test_inverted.png")

# Test 3: Check photo manager pipeline
print("\n=== Testing Photo Manager Pipeline ===")
pm = PhotoManager()
print(f"Photo manager color mode: {pm.display.color_mode}")
print(f"Is color display: {pm.display.is_color_display}")