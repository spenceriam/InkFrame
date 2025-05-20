#!/usr/bin/env python3
"""
Test script for the Waveshare 7.3 inch ACeP 7-color e-ink display.
This script displays a color test pattern on the 7.3 inch ACeP display.

The ACeP (Advanced Color e-Paper) technology supports 7 colors:
- Black
- White
- Red
- Green
- Blue
- Yellow
- Orange

Note: This display has a much longer refresh time compared to 
monochrome or grayscale displays (approximately 35 seconds).
"""
import os
import sys
import time
import logging
from PIL import Image, ImageDraw, ImageFont

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Try to import the Waveshare e-Paper library
try:
    from waveshare_epd import epd7in3f
    SIMULATION_MODE = False
except ImportError:
    logger.warning("Waveshare EPD library not found, running in simulation mode")
    SIMULATION_MODE = True

def create_color_test_pattern(width, height):
    """Create a test pattern demonstrating all 7 colors"""
    # Create a new image with white background
    image = Image.new('RGB', (width, height), (255, 255, 255))
    draw = ImageDraw.Draw(image)
    
    # Define the 7 colors available on ACeP display
    colors = [
        {"name": "Black", "rgb": (0, 0, 0)},
        {"name": "White", "rgb": (255, 255, 255)},
        {"name": "Green", "rgb": (0, 255, 0)},
        {"name": "Blue", "rgb": (0, 0, 255)},
        {"name": "Red", "rgb": (255, 0, 0)},
        {"name": "Yellow", "rgb": (255, 255, 0)},
        {"name": "Orange", "rgb": (255, 128, 0)}
    ]
    
    # Draw color blocks
    block_height = height // 3
    block_width = width // 4
    
    for i, color in enumerate(colors):
        row = i // 4
        col = i % 4
        x1 = col * block_width
        y1 = row * block_height
        x2 = x1 + block_width - 1
        y2 = y1 + block_height - 1
        
        # Draw color block
        draw.rectangle([(x1, y1), (x2, y2)], fill=color["rgb"])
        
        # Add text label (ensure it's visible against the background)
        text_color = (255, 255, 255) if color["name"] in ["Black", "Blue", "Red"] else (0, 0, 0)
        font = ImageFont.load_default()
        text_position = (x1 + block_width//2 - 20, y1 + block_height//2)
        draw.text(text_position, color["name"], font=font, fill=text_color)
    
    # Add title
    draw.rectangle([(0, 2*block_height), (width, height)], fill=(255, 255, 255))
    title_font = ImageFont.load_default()
    draw.text((width//2 - 100, 2*block_height + 20), 
              "7.3 inch ACeP 7-Color Display Test", 
              font=title_font, fill=(0, 0, 0))
    
    # Add instructions
    instructions = [
        "Refresh time: ~35 seconds",
        "Resolution: 800×480 pixels",
        "Note: For best results, use the exact RGB values",
        "shown in the color_test.py script."
    ]
    
    for i, line in enumerate(instructions):
        draw.text((width//2 - 150, 2*block_height + 60 + i*20), 
                 line, font=title_font, fill=(0, 0, 0))
    
    return image

def main():
    """Main function to display color test pattern"""
    logger.info("7.3 inch ACeP 7-Color E-Ink Display Test")
    
    if SIMULATION_MODE:
        # In simulation mode, save the image to a file
        width, height = 800, 480
        logger.info("Running in simulation mode (no display hardware detected)")
        logger.info("Creating test pattern...")
        image = create_color_test_pattern(width, height)
        
        # Save the test pattern
        os.makedirs('simulation', exist_ok=True)
        sim_path = os.path.join('simulation', 'acep_color_test.png')
        image.save(sim_path)
        logger.info(f"Test pattern saved to {sim_path}")
        return
    
    # Initialize the display
    try:
        logger.info("Initializing display...")
        epd = epd7in3f.EPD()
        epd.init()
    except Exception as e:
        logger.error(f"Error initializing display: {e}")
        logger.error("Please check your connections and make sure SPI is enabled.")
        logger.error("You may also need to verify that waveshare_epd library is installed correctly.")
        sys.exit(1)
    
    try:
        # Clear the display
        logger.info("Clearing display... (this may take ~35 seconds)")
        epd.Clear()
        
        # Create test pattern
        logger.info("Creating color test pattern...")
        image = create_color_test_pattern(epd.width, epd.height)
        
        # Display the test pattern
        logger.info("Displaying test pattern... (this may take ~35 seconds)")
        epd.display(epd.getbuffer(image))
        logger.info("Test pattern displayed successfully!")
        
        # Wait before putting the display to sleep
        logger.info("Waiting 5 seconds before sleep...")
        time.sleep(5)
        
        # Put the display to sleep
        logger.info("Putting display to sleep...")
        epd.sleep()
        
    except Exception as e:
        logger.error(f"Error during test: {e}")
        sys.exit(1)
    
    logger.info("Test completed successfully")
    
if __name__ == "__main__":
    main()