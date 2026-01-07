#!/usr/bin/env python3
"""
Simple test script for e-ink display.
Directly tests the connection to the Waveshare e-ink HAT.
"""
import os
import time
import sys

# Add the project root to the Python path
project_root = os.path.abspath(os.path.dirname(__file__))
sys.path.insert(0, project_root)

# Try importing the Waveshare library directly
try:
    # This import varies depending on your display model
    # For 7.5 inch v2
    from waveshare_epd import epd7in5_V2 as epd
    print("Successfully imported Waveshare EPD library")

    # Initialize the display
    print("Initializing display...")
    display = epd.EPD()
    display.init()
    
    # Clear the display
    print("Clearing display...")
    display.Clear()
    
    # Import Pillow for image creation
    from PIL import Image, ImageDraw, ImageFont
    
    # Create a simple test image
    print("Creating test image...")
    image = Image.new('1', (display.width, display.height), 255)  # 255: white
    draw = ImageDraw.Draw(image)
    
    # Draw a black border
    draw.rectangle([(0, 0), (display.width-1, display.height-1)], outline=0)
    
    # Draw some text
    font = ImageFont.load_default()
    draw.text((display.width//4, display.height//2), 'Hello, E-Ink Display!', font=font, fill=0)
    
    # Display the image
    print("Displaying image...")
    display.display(display.getbuffer(image))
    
    print("Test complete! You should see content on the display.")
    print("Entering sleep mode in 5 seconds...")
    time.sleep(5)
    
    # Put display to sleep
    display.sleep()
    print("Display sleeping.")
    
except ImportError as e:
    print(f"Failed to import Waveshare library: {e}")
    print("Make sure the library is installed correctly")
    print("\nTrying to install the library...")
    
    try:
        print("Cloning Waveshare library...")
        os.system("git clone https://github.com/waveshare/e-Paper.git waveshare_repo")
        
        print("Creating Waveshare e-Paper directory...")
        os.makedirs("waveshare_epd", exist_ok=True)
        
        print("Copying library files...")
        os.system("cp -r waveshare_repo/RaspberryPi_JetsonNano/python/lib/waveshare_epd/*.py waveshare_epd/")
        
        print("Cleaning up...")
        os.system("rm -rf waveshare_repo")
        
        print("\nLibrary installation complete. Please run this script again.")
    except Exception as install_error:
        print(f"Error installing library: {install_error}")
    
except Exception as e:
    print(f"Error during display test: {e}")