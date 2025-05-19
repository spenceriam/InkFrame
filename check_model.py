#!/usr/bin/env python3
"""
Script to test different Waveshare e-ink display models.
This helps identify which model works with your specific hardware.
"""
import os
import sys
import time
import traceback

# Models to try, in order of likelihood for 7.5" displays
MODELS_TO_TRY = [
    ("epd7in5_V2", "7.5 inch V2 (800×480)"),
    ("epd7in5", "7.5 inch (640×384)"),
    ("epd7in5_HD", "7.5 inch HD"),
    ("epd7in5b_V2", "7.5 inch B/W/Red V2")
]

def test_model(module_name, display_name):
    """Test a specific display model"""
    print(f"\n----- Testing {display_name} ({module_name}) -----")
    
    try:
        # Dynamically import the module
        print(f"Importing {module_name}...")
        epd_module = __import__(f"waveshare_epd.{module_name}", fromlist=["*"])
        print(f"Successfully imported {module_name}")
        
        # Print dimensions
        width = getattr(epd_module, "EPD_WIDTH", "unknown")
        height = getattr(epd_module, "EPD_HEIGHT", "unknown")
        print(f"Display dimensions: {width}x{height}")
        
        # Initialize display
        print("Creating EPD object...")
        epd = epd_module.EPD()
        print("Initializing display (this may take a few seconds)...")
        epd.init()
        print("Successfully initialized display!")
        
        # Clear display
        print("Clearing display...")
        epd.Clear()
        print("Display cleared")
        
        # Create test image
        print("Creating test image...")
        from PIL import Image, ImageDraw, ImageFont
        
        # Get dimensions from the object, not the module (more reliable)
        image = Image.new('1', (epd.width, epd.height), 255)
        draw = ImageDraw.Draw(image)
        
        # Draw a border and text
        draw.rectangle([(0, 0), (epd.width-1, epd.height-1)], outline=0)
        font = ImageFont.load_default()
        text = f"Model: {module_name}"
        draw.text((epd.width//4, epd.height//2), text, font=font, fill=0)
        
        # Display image
        print("Displaying test image...")
        epd.display(epd.getbuffer(image))
        print("Image displayed!")
        
        # Wait and sleep
        print("Waiting 5 seconds...")
        time.sleep(5)
        print("Putting display to sleep...")
        epd.sleep()
        
        print(f"\n✓ SUCCESS: {module_name} is compatible with your display!")
        return True
        
    except ImportError:
        print(f"✗ Module {module_name} not found")
        return False
    except Exception as e:
        print(f"✗ Error with {module_name}: {e}")
        print(traceback.format_exc())
        return False

def main():
    """Test each model until one works"""
    print("E-ink Display Model Checker")
    print("This script will test different Waveshare display models to find which one works")
    
    success = False
    
    # Try each model
    for module_name, display_name in MODELS_TO_TRY:
        result = test_model(module_name, display_name)
        if result:
            success = True
            print(f"\nCompatible model found: {module_name} ({display_name})")
            print(f"Please use this model in your application.")
            break
    
    if not success:
        print("\nNo compatible models found.")
        print("Please check your connections and make sure SPI is enabled.")
        print("You may also need to specify a different display model.")

if __name__ == "__main__":
    main()