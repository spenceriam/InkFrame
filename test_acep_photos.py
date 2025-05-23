#!/usr/bin/env python3
"""
Test script to diagnose photo display issues on 7.3" ACeP color display
"""
import os
import logging
from PIL import Image
from src.display.photo_manager import PhotoManager
from src.utils.image_processor import ImageProcessor

logging.basicConfig(level=logging.DEBUG)
logger = logging.getLogger(__name__)

def test_photo_processing():
    """Test how photos are processed for the ACeP display"""
    
    # Load configuration
    config = {
        "display": {
            "type": "7in3f",
            "color_mode": "color",
            "enable_dithering": True,
            "dithering_method": "floydsteinberg",
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
    
    # Get a sample photo
    photo_dir = config["photos"]["directory"]
    photos = [f for f in os.listdir(photo_dir) if f.lower().endswith(('.jpg', '.jpeg', '.png', '.bmp'))]
    
    if not photos:
        logger.error("No photos found in directory")
        return
    
    # Process the first photo
    test_photo = os.path.join(photo_dir, photos[0])
    logger.info(f"Testing with photo: {test_photo}")
    
    # Load and examine the photo
    original = Image.open(test_photo)
    logger.info(f"Original image: mode={original.mode}, size={original.size}")
    
    # Process it for color display
    logger.info("Processing image for ACeP display...")
    processed_path = processor.preprocess_image(test_photo, "test_acep_output.bmp", mode="color")
    
    if processed_path:
        # Examine the processed image
        processed = Image.open(processed_path)
        logger.info(f"Processed image: mode={processed.mode}, size={processed.size}")
        
        # Count unique colors
        unique_colors = set()
        width, height = processed.size
        pixels = processed.load()
        
        for y in range(0, height, 10):  # Sample every 10th pixel for speed
            for x in range(0, width, 10):
                unique_colors.add(pixels[x, y])
        
        logger.info(f"Unique colors in processed image: {len(unique_colors)}")
        logger.info(f"Colors found: {sorted(list(unique_colors))}")
        
        # Expected ACeP colors
        expected = [
            (0, 0, 0),      # Black
            (255, 255, 255), # White
            (0, 255, 0),    # Green
            (0, 0, 255),    # Blue
            (255, 0, 0),    # Red
            (255, 255, 0),  # Yellow
            (255, 128, 0)   # Orange
        ]
        
        logger.info(f"Expected ACeP colors: {expected}")
        
        # Check if all colors are valid ACeP colors
        invalid_colors = [c for c in unique_colors if c not in expected]
        if invalid_colors:
            logger.warning(f"Found {len(invalid_colors)} invalid colors: {invalid_colors[:5]}...")
        else:
            logger.info("All colors are valid ACeP colors!")

def test_display_directly():
    """Test displaying on the actual hardware"""
    logger.info("\nTesting direct display...")
    
    # Create a simple test image with ACeP colors
    test_img = Image.new('RGB', (800, 480), (255, 255, 255))
    pixels = test_img.load()
    
    # Draw stripes of each ACeP color
    colors = [
        (0, 0, 0),      # Black
        (255, 255, 255), # White
        (255, 0, 0),    # Red
        (0, 255, 0),    # Green
        (0, 0, 255),    # Blue
        (255, 255, 0),  # Yellow
        (255, 128, 0)   # Orange
    ]
    
    stripe_width = 800 // len(colors)
    for i, color in enumerate(colors):
        x_start = i * stripe_width
        x_end = (i + 1) * stripe_width
        for x in range(x_start, x_end):
            for y in range(480):
                pixels[x, y] = color
    
    # Save test image
    test_img.save("test_acep_stripes.bmp")
    logger.info("Created test stripe image")
    
    # Try to display it
    try:
        from src.display.eink_driver import EInkDisplay
        display = EInkDisplay(display_type="7in3f", color_mode="color")
        
        if display.initialized:
            logger.info("Displaying test stripes...")
            display.display_image_buffer(test_img, force_full_refresh=True)
            logger.info("Display complete!")
        else:
            logger.error("Display not initialized")
    except Exception as e:
        logger.error(f"Error displaying: {e}")

if __name__ == "__main__":
    import sys
    
    if len(sys.argv) > 1 and sys.argv[1] == "display":
        test_display_directly()
    else:
        test_photo_processing()
        logger.info("\nTo test actual display, run: python test_acep_photos.py display")