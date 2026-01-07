#!/usr/bin/env python3
"""
Debug script to check display status and test basic functionality
"""
import os
import json
import logging
from PIL import Image, ImageDraw, ImageFont

logging.basicConfig(level=logging.DEBUG)
logger = logging.getLogger(__name__)

def check_config():
    """Check configuration status"""
    config_path = "config/config.json"
    if os.path.exists(config_path):
        with open(config_path, 'r') as f:
            config = json.load(f)
        
        # Check weather config
        weather = config.get('weather', {})
        api_key = weather.get('api_key', '')
        city = weather.get('city', '')
        
        logger.info("Configuration Check:")
        logger.info(f"  Config file: {config_path}")
        logger.info(f"  Display type: {config['display'].get('type', 'not set')}")
        logger.info(f"  Color mode: {config['display'].get('color_mode', 'not set')}")
        logger.info(f"  Weather API key: {'SET' if api_key else 'NOT SET'}")
        logger.info(f"  Weather location: {city if city else 'NOT SET'}")
        logger.info(f"  Photo directory: {config['photos'].get('directory', 'not set')}")
        
        return config
    else:
        logger.error(f"Config file not found at {config_path}")
        return None

def test_simple_display():
    """Test displaying a simple image"""
    try:
        from src.display.eink_driver import EInkDisplay
        
        logger.info("\nTesting display initialization...")
        display = EInkDisplay(display_type="7in3f", color_mode="color")
        
        if not display.initialized:
            logger.error("Display failed to initialize!")
            return False
        
        logger.info("Display initialized successfully")
        
        # Create a simple test image
        logger.info("Creating test image...")
        img = Image.new('RGB', (display.width, display.height), (255, 255, 255))
        draw = ImageDraw.Draw(img)
        
        # Draw some text
        draw.text((100, 100), "InkFrame Test", fill=(0, 0, 0))
        draw.text((100, 150), "If you see this, display is working!", fill=(255, 0, 0))
        
        # Draw colored rectangles
        colors = [(255, 0, 0), (0, 255, 0), (0, 0, 255), (255, 255, 0)]
        for i, color in enumerate(colors):
            x = 100 + i * 150
            draw.rectangle([(x, 250), (x + 100, 350)], fill=color)
        
        # Display the image
        logger.info("Displaying test image...")
        success = display.display_image_buffer(img, force_full_refresh=True)
        
        if success:
            logger.info("Test image displayed successfully!")
        else:
            logger.error("Failed to display test image")
        
        # Clean up
        display.sleep()
        display.close()
        
        return success
        
    except Exception as e:
        logger.error(f"Error during display test: {e}")
        import traceback
        traceback.print_exc()
        return False

def check_photos():
    """Check if photos are available"""
    photo_dir = "static/images/photos"
    if os.path.exists(photo_dir):
        photos = [f for f in os.listdir(photo_dir) if f.lower().endswith(('.jpg', '.jpeg', '.png', '.bmp'))]
        logger.info(f"\nPhoto directory check:")
        logger.info(f"  Directory: {photo_dir}")
        logger.info(f"  Photos found: {len(photos)}")
        if photos:
            logger.info(f"  First few photos: {photos[:3]}")
    else:
        logger.error(f"Photo directory not found: {photo_dir}")

def test_weather():
    """Test weather client"""
    config = check_config()
    if config:
        try:
            from src.weather.weather_client import WeatherClient
            
            logger.info("\nTesting weather client...")
            weather_client = WeatherClient(config)
            weather_data = weather_client.get_weather()
            
            if weather_data:
                logger.info("Weather data retrieved:")
                logger.info(f"  Temperature: {weather_data.get('temp', 'N/A')}")
                logger.info(f"  Condition: {weather_data.get('condition', 'N/A')}")
                logger.info(f"  Humidity: {weather_data.get('humidity', 'N/A')}%")
            else:
                logger.warning("No weather data returned - check API key and location")
                
        except Exception as e:
            logger.error(f"Error testing weather: {e}")

if __name__ == "__main__":
    import sys
    
    print("InkFrame Display Debug Tool")
    print("=" * 40)
    
    # Check configuration
    config = check_config()
    
    # Check photos
    check_photos()
    
    # Test weather
    test_weather()
    
    # Ask if user wants to test display
    if len(sys.argv) > 1 and sys.argv[1] == "--display":
        print("\nTesting display (this will take ~35 seconds)...")
        test_simple_display()
    else:
        print("\nTo test the display, run: python3 debug_display.py --display")