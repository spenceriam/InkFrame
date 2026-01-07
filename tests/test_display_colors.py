#!/usr/bin/env python3
"""
Test if display can show colors
"""
import time
from PIL import Image
from waveshare_epd import epd7in3f

print("Testing 7.3inch color display directly...")

try:
    # Initialize display
    epd = epd7in3f.EPD()
    epd.init()
    
    print("Display initialized")
    print(f"Size: {epd.width}x{epd.height}")
    
    # Create color test pattern
    img = Image.new('RGB', (epd.width, epd.height), (255, 255, 255))
    
    # Draw colored rectangles
    colors = [
        ((0, 0, 0), "Black"),
        ((255, 0, 0), "Red"),
        ((0, 255, 0), "Green"),
        ((0, 0, 255), "Blue"),
        ((255, 255, 0), "Yellow"),
        ((255, 128, 0), "Orange"),
        ((255, 255, 255), "White")
    ]
    
    rect_width = epd.width // len(colors)
    
    for i, (color, name) in enumerate(colors):
        x1 = i * rect_width
        x2 = (i + 1) * rect_width
        
        # Fill rectangle
        for x in range(x1, x2):
            for y in range(100, 300):
                img.putpixel((x, y), color)
    
    print("Displaying color test pattern...")
    print("This should show 7 colored bars")
    
    # Display it
    epd.display(epd.getbuffer(img))
    
    print("Display complete!")
    print("\nYou should see:")
    print("- Black bar")
    print("- Red bar") 
    print("- Green bar")
    print("- Blue bar")
    print("- Yellow bar")
    print("- Orange bar")
    print("- White bar")
    
    time.sleep(5)
    
    # Sleep display
    epd.sleep()
    
except Exception as e:
    print(f"Error: {e}")
    import traceback
    traceback.print_exc()