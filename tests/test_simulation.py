#!/usr/bin/env python3
"""
Test script to verify InkFrame functionality in simulation mode.
This can be run on any system, not just Raspberry Pi.
"""
import os
import sys
import logging
import time

# Add the project root to the Python path
project_root = os.path.abspath(os.path.join(os.path.dirname(__file__), '..'))
sys.path.insert(0, project_root)

from src.utils.config_manager import ConfigManager
from src.utils.image_processor import ImageProcessor
from src.display.eink_driver import EInkDisplay
from src.display.photo_manager import PhotoManager

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def test_config_manager():
    """Test the configuration manager"""
    logger.info("Testing ConfigManager...")
    
    config_manager = ConfigManager()
    config = config_manager.config
    
    logger.info(f"Loaded configuration with {len(config)} sections")
    logger.info(f"Display settings: rotation_interval_minutes = {config['display']['rotation_interval_minutes']}")
    
    # Test updating a setting
    original_value = config_manager.get('display.rotation_interval_minutes')
    test_value = 30
    
    config_manager.set('display.rotation_interval_minutes', test_value)
    new_value = config_manager.get('display.rotation_interval_minutes')
    
    assert new_value == test_value, f"Failed to update setting: expected {test_value}, got {new_value}"
    
    # Restore original value
    config_manager.set('display.rotation_interval_minutes', original_value)
    
    logger.info("ConfigManager test passed")

def test_eink_driver():
    """Test the e-ink display driver (simulation mode)"""
    logger.info("Testing EInkDisplay in simulation mode...")
    
    display = EInkDisplay()
    
    # Check initialization
    assert display.initialized, "Display initialization failed"
    
    # Test clearing the display
    assert display.clear(), "Display clear failed"
    
    # Create a test image
    from PIL import Image, ImageDraw, ImageFont
    image = Image.new('1', (display.width, display.height), 255)  # white
    draw = ImageDraw.Draw(image)
    draw.rectangle([(50, 50), (display.width - 50, display.height - 50)], outline=0)
    draw.text((100, 100), "InkFrame Test", fill=0)
    
    # Test displaying the image
    assert display.display_image_buffer(image), "Display image failed"
    
    # Check if simulation file was created
    sim_file = os.path.join('simulation', 'current_display.png')
    assert os.path.exists(sim_file), f"Simulation file not created at {sim_file}"
    
    logger.info(f"Test image saved to {sim_file}")
    logger.info("EInkDisplay test passed")

def test_photo_manager():
    """Test the photo manager"""
    logger.info("Testing PhotoManager...")
    
    # Create test photos directory
    os.makedirs('static/images/photos', exist_ok=True)
    
    # Create a test photo if none exist
    photo_files = [f for f in os.listdir('static/images/photos') 
                  if f.lower().endswith(('.png', '.jpg', '.jpeg', '.bmp'))]
    
    if not photo_files:
        logger.info("No photos found, creating a test photo")
        from PIL import Image, ImageDraw
        test_img = Image.new('RGB', (800, 480), color='white')
        draw = ImageDraw.Draw(test_img)
        draw.rectangle([(50, 50), (750, 430)], outline='black')
        draw.text((300, 200), "TEST PHOTO", fill='black')
        test_img.save('static/images/photos/test_photo.png')
    
    # Initialize the photo manager
    photo_manager = PhotoManager()
    
    # Test random photo selection
    photo = photo_manager.get_random_photo()
    assert photo is not None, "Failed to get a random photo"
    logger.info(f"Selected photo: {photo}")
    
    # Test display
    assert photo_manager.display_photo(photo), "Failed to display photo"
    
    logger.info("PhotoManager test passed")

def main():
    """Run all tests"""
    logger.info("Starting InkFrame simulation tests")
    
    # Ensure simulation directory exists
    os.makedirs('simulation', exist_ok=True)
    
    try:
        test_config_manager()
        test_eink_driver()
        test_photo_manager()
        
        logger.info("All tests passed!")
        logger.info("InkFrame is working correctly in simulation mode")
        logger.info("Check the 'simulation' directory for output images")
        
    except Exception as e:
        logger.error(f"Test failed: {e}")
        return 1
    
    return 0

if __name__ == "__main__":
    sys.exit(main())