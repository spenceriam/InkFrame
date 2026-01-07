#!/usr/bin/env python3
"""
Check what the processed image looks like
"""
import os
from PIL import Image
from src.utils.image_processor import ImageProcessor

# Get config
config = {
    "display": {
        "type": "7in3f",
        "color_mode": "color",
        "enable_dithering": True,
        "contrast_factor": 1.2,
        "brightness_factor": 1.1,
        "sharpness_factor": 1.2
    },
    "photos": {
        "directory": "static/images/photos",
        "max_width": 800,
        "max_height": 440,
        "format": "bmp"
    }
}

processor = ImageProcessor(config)

# Find a photo
photo_dir = "static/images/photos"
photos = [f for f in os.listdir(photo_dir) if f.lower().endswith(('.jpg', '.jpeg', '.png', '.bmp'))]

if photos:
    test_photo = os.path.join(photo_dir, photos[0])
    print(f"Processing: {test_photo}")
    
    # Process it
    output = processor.preprocess_image(test_photo, "test_processed.bmp", mode="color")
    
    if output:
        # Check the image
        img = Image.open(output)
        print(f"Processed image: {img.size}, mode={img.mode}")
        
        # Count colors
        pixels = img.getdata()
        unique_colors = set(pixels)
        print(f"Unique colors: {len(unique_colors)}")
        print(f"First 10 colors: {list(unique_colors)[:10]}")
        
        # Save a PNG for viewing
        img.save("test_processed.png")
        print("Saved test_processed.png for inspection")
else:
    print("No photos found!")