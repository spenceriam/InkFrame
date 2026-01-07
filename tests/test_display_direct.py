#!/usr/bin/env python3
"""
Direct display test bypassing all our code
"""
import time
import logging
from PIL import Image, ImageDraw

logging.basicConfig(level=logging.DEBUG)

try:
    # Import the Waveshare driver directly
    from waveshare_epd import epd7in3f
    
    print("Initializing display...")
    epd = epd7in3f.EPD()
    epd.init()
    
    print("Creating simple test image...")
    # Create a simple white image with black text
    image = Image.new('RGB', (epd.width, epd.height), (255, 255, 255))
    draw = ImageDraw.Draw(image)
    
    # Draw a black rectangle
    draw.rectangle([(100, 100), (700, 380)], fill=(0, 0, 0))
    
    # Draw white text on black
    draw.text((200, 200), "DISPLAY TEST", fill=(255, 255, 255))
    draw.text((200, 250), "If you see this, hardware is OK", fill=(255, 255, 255))
    
    print(f"Displaying test image on {epd.width}x{epd.height} display...")
    print("This will take about 35 seconds...")
    
    # Display the image
    epd.display(epd.getbuffer(image))
    
    print("Display complete! Waiting 5 seconds...")
    time.sleep(5)
    
    print("Putting display to sleep...")
    epd.sleep()
    
    print("Test complete!")
    
except Exception as e:
    print(f"Error: {e}")
    import traceback
    traceback.print_exc()