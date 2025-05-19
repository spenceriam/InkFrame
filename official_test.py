#!/usr/bin/python
# -*- coding:utf-8 -*-
"""
Modified version of the official Waveshare test script for 7.5" B/W V2 display
Adapted to work with InkFrame project structure
"""
import sys
import os
import logging
import time
import traceback
from PIL import Image, ImageDraw, ImageFont

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def run_test():
    """Run the official Waveshare test script"""
    try:
        logger.info("Starting official Waveshare test script")
        
        # Try to import the Waveshare library
        try:
            # First try the black/white/red 7.5" V2 model
            from waveshare_epd import epd7in5b_V2
            model_name = "epd7in5b_V2"
            logger.info(f"Using {model_name} driver")
        except ImportError:
            try:
                # Then try the black/white 7.5" V2 model
                from waveshare_epd import epd7in5_V2
                model_name = "epd7in5_V2"
                logger.info(f"Using {model_name} driver")
                # Monkey patch to match the B/W/R version's API
                epd7in5_V2.EPD.display = lambda self, black, _: self.display(black)
            except ImportError:
                try:
                    # Then try the regular 7.5" model
                    from waveshare_epd import epd7in5
                    model_name = "epd7in5"
                    logger.info(f"Using {model_name} driver")
                    # Monkey patch to match the B/W/R version's API
                    epd7in5.EPD.display = lambda self, black, _: self.display(black)
                except ImportError:
                    logger.error("Could not import any 7.5 inch display drivers")
                    logger.info("Please install the Waveshare library first")
                    return False

        # Get the appropriate module based on which one was imported
        if model_name == "epd7in5b_V2":
            epd_module = epd7in5b_V2
        elif model_name == "epd7in5_V2":
            epd_module = epd7in5_V2
        else:
            epd_module = epd7in5

        # Initialize the display
        logger.info("Initializing display...")
        epd = epd_module.EPD()
        logger.info("Clearing display...")
        epd.init()
        epd.Clear()

        # Load font
        default_font = ImageFont.load_default()
        font24 = default_font
        font18 = default_font
        
        # Try to use a nicer font if available
        try:
            font_path = "/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf"
            if os.path.exists(font_path):
                font24 = ImageFont.truetype(font_path, 24)
                font18 = ImageFont.truetype(font_path, 18)
        except:
            pass
        
        # Test 1: Draw on the horizontal image
        logger.info("1. Drawing on the horizontal image...")
        Himage = Image.new('1', (epd.width, epd.height), 255)  # 255: clear the frame (white)
        Other = Image.new('1', (epd.width, epd.height), 255)   # 255: clear the frame (white)
        
        draw_Himage = ImageDraw.Draw(Himage)
        draw_other = ImageDraw.Draw(Other)
        
        # Add text and shapes to the images
        draw_Himage.text((10, 0), 'InkFrame Test', font=font24, fill=0)
        draw_Himage.text((10, 30), f'Model: {model_name}', font=font24, fill=0)
        draw_Himage.text((10, 60), f'Size: {epd.width}x{epd.height}', font=font18, fill=0)
        
        # Draw some shapes
        draw_other.rectangle((50, 120, 150, 220), outline=0)
        draw_Himage.rectangle((200, 120, 300, 220), fill=0)
        draw_other.ellipse((350, 120, 450, 220), outline=0)
        draw_Himage.ellipse((500, 120, 600, 220), fill=0)
        
        # Display the images
        logger.info("Displaying test pattern...")
        epd.display(epd.getbuffer(Himage), epd.getbuffer(Other))
        logger.info("Display updated. Check your e-ink screen for the test pattern.")
        
        # Wait to allow viewing the results
        logger.info("Waiting 10 seconds...")
        time.sleep(10)
        
        # Clear the display
        logger.info("Clearing display...")
        epd.init()
        epd.Clear()
        
        # Sleep
        logger.info("Putting display to sleep...")
        epd.sleep()
        
        logger.info("Test completed successfully!")
        return True
        
    except Exception as e:
        logger.error(f"Error during test: {e}")
        logger.error(traceback.format_exc())
        return False

if __name__ == "__main__":
    success = run_test()
    if success:
        print("\n✅ Test PASSED! Your e-ink display is working correctly.")
    else:
        print("\n❌ Test FAILED! Check the error messages above.")
        print("\nTroubleshooting tips:")
        print("1. Ensure SPI is enabled: sudo raspi-config -> Interface Options -> SPI -> Enable")
        print("2. Check physical connections between Raspberry Pi and e-ink HAT")
        print("3. Verify the Waveshare library is installed in the waveshare_epd directory")
        print("4. Try a different display model in check_model.py")