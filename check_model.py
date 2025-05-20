#!/usr/bin/env python3
"""
Script to test different Waveshare e-ink display models.
This helps identify which model works with your specific hardware.
"""
import os
import sys
import time
import traceback

# Models to try, in order of likelihood for 7.3-7.5" displays
MODELS_TO_TRY = [
    ("epd7in5_V2", "7.5 inch V2 (800×480)"),
    ("epd7in3f", "7.3 inch ACeP 7-Color (800×480)"),
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
        
        # Determine if this is a color display
        is_color_display = "f" in module_name.lower()  # ACeP models have 'f' suffix
        
        if is_color_display:
            # For color displays, create RGB image
            print("Creating color test image...")
            image = Image.new('RGB', (epd.width, epd.height), (255, 255, 255))
            draw = ImageDraw.Draw(image)
            
            # Draw color blocks
            colors = [
                (0, 0, 0),      # Black
                (255, 0, 0),    # Red
                (0, 255, 0),    # Green
                (0, 0, 255),    # Blue
                (255, 255, 0),  # Yellow
                (255, 128, 0)   # Orange
            ]
            
            block_width = epd.width // len(colors)
            for i, color in enumerate(colors):
                x1 = i * block_width
                x2 = (i + 1) * block_width
                draw.rectangle([(x1, 100), (x2, 300)], fill=color)
            
            # Draw border and text
            draw.rectangle([(0, 0), (epd.width-1, epd.height-1)], outline=(0, 0, 0))
            font = ImageFont.load_default()
            text = f"7-Color Model: {module_name}"
            draw.text((epd.width//4, epd.height//2 + 100), text, font=font, fill=(0, 0, 0))
        else:
            # For B&W displays, create 1-bit image
            image = Image.new('1', (epd.width, epd.height), 255)
            draw = ImageDraw.Draw(image)
            
            # Draw a border and text
            draw.rectangle([(0, 0), (epd.width-1, epd.height-1)], outline=0)
            font = ImageFont.load_default()
            text = f"Model: {module_name}"
            draw.text((epd.width//4, epd.height//2), text, font=font, fill=0)
        
        # Display image
        print("Displaying test image...")
        
        # Update based on display type
        if is_color_display:
            print("Using color display method...")
            # ACeP color displays use a different buffer method
            epd.display(epd.getbuffer(image))
        else:
            # Standard B&W or grayscale displays
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