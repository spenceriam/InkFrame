#!/usr/bin/env python3
"""
Test the full display with photo and status bar
"""
import logging
from PIL import Image, ImageDraw
from src.display.photo_manager import PhotoManager

logging.basicConfig(level=logging.INFO)

print("Testing full display with status bar...")

try:
    # Create photo manager
    pm = PhotoManager()
    
    # Create a test image that fills the photo area
    photo_width = pm.display.width  # 800
    photo_height = pm.display.height - pm.config["display"]["status_bar_height"]  # 480 - 40 = 440
    
    print(f"Creating test photo: {photo_width}x{photo_height}")
    
    # Create a colorful test pattern
    test_photo = Image.new('RGB', (photo_width, photo_height), (255, 255, 255))
    draw = ImageDraw.Draw(test_photo)
    
    # Draw colored stripes
    colors = [(255, 0, 0), (0, 255, 0), (0, 0, 255), (255, 255, 0), (255, 128, 0)]
    stripe_width = photo_width // len(colors)
    
    for i, color in enumerate(colors):
        x1 = i * stripe_width
        x2 = (i + 1) * stripe_width
        draw.rectangle([(x1, 0), (x2, photo_height)], fill=color)
    
    # Add text
    draw.text((photo_width//2 - 100, photo_height//2), "TEST PHOTO", fill=(0, 0, 0))
    
    # Save test photo
    test_photo.save("test_fullsize_photo.bmp")
    print("Saved test photo")
    
    # Display it using photo manager
    print("\nDisplaying through photo manager...")
    result = pm.display_photo("test_fullsize_photo.bmp", force_refresh=True)
    
    if result:
        print("Display successful!")
        print("You should see:")
        print("- Colored stripes with 'TEST PHOTO' text")
        print("- Status bar at bottom with time and weather")
    else:
        print("Display failed!")
        
except Exception as e:
    print(f"Error: {e}")
    import traceback
    traceback.print_exc()