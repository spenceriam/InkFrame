#!/usr/bin/env python3
"""
Test our display driver with a processed image
"""
import logging
from PIL import Image
from src.display.eink_driver import EInkDisplay

logging.basicConfig(level=logging.DEBUG)

print("Testing our display driver...")

# Initialize our display driver
display = EInkDisplay(display_type="7in3f", color_mode="color")

if not display.initialized:
    print("ERROR: Display failed to initialize!")
    exit(1)

print("Display initialized successfully")

# Load the processed image we just created
try:
    img = Image.open("test_processed.bmp")
    print(f"Loaded image: {img.size}, mode={img.mode}")
    
    print("Displaying image through our driver...")
    result = display.display_image_buffer(img, force_full_refresh=True)
    
    if result:
        print("Display completed successfully!")
    else:
        print("Display failed!")
        
except Exception as e:
    print(f"Error: {e}")
    import traceback
    traceback.print_exc()
finally:
    print("Cleaning up...")
    display.sleep()
    display.close()