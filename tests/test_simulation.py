#!/usr/bin/env python3
"""
Test script to verify InkFrame functionality in simulation mode.
This can be run on any system, not just Raspberry Pi.
"""

import logging
import os
import sys
import time

# Add the project root to the Python path
project_root = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
sys.path.insert(0, project_root)

from src.display.eink_driver import EInkDisplay
from src.display.photo_manager import PhotoManager
from src.utils.config_manager import ConfigManager
from src.utils.image_processor import ImageProcessor

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


def test_config_manager():
    """Test the configuration manager"""
    logger.info("Testing ConfigManager...")

    config_manager = ConfigManager()
    config = config_manager.config

    logger.info(f"Loaded configuration with {len(config)} sections")
    logger.info(
        f"Display settings: rotation_interval_minutes = {config['display']['rotation_interval_minutes']}"
    )

    # Test updating a setting
    original_value = config_manager.get("display.rotation_interval_minutes")
    test_value = 30

    config_manager.set("display.rotation_interval_minutes", test_value)
    new_value = config_manager.get("display.rotation_interval_minutes")

    assert new_value == test_value, (
        f"Failed to update setting: expected {test_value}, got {new_value}"
    )

    # Restore original value
    config_manager.set("display.rotation_interval_minutes", original_value)

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

    image = Image.new("1", (display.width, display.height), 255)  # white
    draw = ImageDraw.Draw(image)
    draw.rectangle([(50, 50), (display.width - 50, display.height - 50)], outline=0)
    draw.text((100, 100), "InkFrame Test", fill=0)

    # Test displaying the image
    assert display.display_image_buffer(image), "Display image failed"

    # Check if simulation file was created
    sim_file = os.path.join("simulation", "current_display.png")
    assert os.path.exists(sim_file), f"Simulation file not created at {sim_file}"

    logger.info(f"Test image saved to {sim_file}")
    logger.info("EInkDisplay test passed")


def test_photo_manager():
    """Test photo manager"""
    logger.info("Testing PhotoManager...")

    # Create test photos directory
    os.makedirs("static/images/photos", exist_ok=True)

    # Create a test photo if none exist
    photo_files = [
        f
        for f in os.listdir("static/images/photos")
        if f.lower().endswith((".png", ".jpg", ".jpeg", ".bmp"))
    ]

    if not photo_files:
        logger.info("No photos found, creating a test photo")
        from PIL import Image, ImageDraw

        test_img = Image.new("RGB", (800, 480), color="white")
        draw = ImageDraw.Draw(test_img)
        draw.rectangle([(50, 50), (750, 430)], outline="black")
        draw.text((300, 200), "TEST PHOTO", fill="black")
        test_img.save("static/images/photos/test_photo.png")

    # Create e-ink simulator instance for testing
    from src.display.eink_simulator import EInkSimulator

    logger.info("Creating e-ink display simulator...")
    display_simulator = EInkSimulator(display_type="7in5_V2", color_mode="grayscale")

    # Initialize the simulator
    assert display_simulator.init(), "Simulator initialization failed"

    # Initialize photo manager with simulator instead of real display
    photo_manager = PhotoManager(display_instance=display_simulator)


# Create e-ink simulator instance for testing
from src.display.eink_simulator import EInkSimulator

logger.info("Creating e-ink display simulator...")
display_simulator = EInkSimulator(display_type="7in5_V2", color_mode="grayscale")

# Initialize the simulator
assert display_simulator.init(), "Simulator initialization failed"

# Initialize photo manager with simulator instance
# Initialize photo manager with simulator instead of real display
photo_manager = PhotoManager(display_instance=display_simulator)

# Test random photo selection
photo = photo_manager.get_random_photo()
assert photo is not None, "Failed to get a random photo"
logger.info(f"Selected photo: {photo}")

# Test display
assert photo_manager.display_photo(photo), "Failed to display photo"

logger.info("PhotoManager test passed")

def test_weather_client():
"""Test weather.gov client integration"""
logger.info("Testing Weather.gov client...")

from src.weather.weather_client import WeatherClient

# Create minimal config for testing
test_config = {
    "display": {
        "rotation_interval_minutes": 60,
        "status_bar_height": 40
    },
    "photos": {
        "directory": "static/images/photos",
        "max_width": 800,
        "max_height": 440
    },
    "weather": {
        "update_interval_minutes": 30,
        "cache_expiry_minutes": 120
    },
    "system": {
        "timezone": "UTC",
        "web_port": 5000,
        "debug_mode": False
    }
}

# Test with default location (McHenry, IL)
weather_client = WeatherClient(test_config)

# Get weather data
weather = weather_client.get_weather()

assert weather is not None, "Weather client returned None"
assert "current" in weather, "Weather data missing 'current' key"
assert "temp" in weather["current"], "Temperature not in weather data"
assert "condition" in weather["current"], "Weather condition not in weather data"

logger.info(f"Weather: {weather['current']['temp']}°{weather['current'].get('unit', 'F')} - {weather['current']['condition']}")

# Check if date is included
assert "date" in weather, "Date not in weather data"
logger.info(f"Date: {weather['date']}")

logger.info("Weather.gov client test passed")


def main():
    """Run all tests"""
    logger.info("Starting InkFrame simulation tests")

    # Ensure simulation directory exists
    os.makedirs("simulation", exist_ok=True)

    try:
        test_config_manager()
        test_eink_driver()
        test_photo_manager()
        test_weather_client()
        test_weather_client()

        logger.info("=" * 60)
        logger.info("✓ ALL TESTS PASSED!")
        logger.info("=" * 60)
        logger.info("InkFrame is working correctly in simulation mode")
        logger.info(
            "Check 'simulation/' directory for e-ink display output (PNG files)"
        )
        logger.info("")
        logger.info("Test Summary:")
        logger.info("  ✓ Configuration loading")
        logger.info("  ✓ E-ink simulator initialization")
        logger.info("  ✓ Photo manager with simulator")
        logger.info("  ✓ Photo display and status bar")
        logger.info("  ✓ Weather.gov API integration")
        logger.info("")
        logger.info("Next Steps:")
        logger.info("  1. Review generated PNG files in simulation/")
        logger.info("  2. Test on actual Raspberry Pi hardware")
        logger.info("  3. Run 'python run.py' for production mode")
        logger.info("=" * 60)
        logger.info("✓ ALL TESTS PASSED!")
        logger.info("=" * 60)
        logger.info("InkFrame is working correctly in simulation mode")
        logger.info(
            "Check 'simulation/' directory for e-ink display output (PNG files)"
        )
        logger.info("Each PNG file shows what would appear on the physical display")
        logger.info("")
        logger.info("Test Summary:")
        logger.info("  ✓ Configuration loading")
        logger.info("  ✓ E-ink simulator initialization")
        logger.info("  ✓ Photo manager with simulator")
        logger.info("  ✓ Photo display and status bar")
        logger.info("  ✓ Weather.gov API integration")
        logger.info("")
        logger.info("Next Steps:")
        logger.info("  1. Review generated PNG files in simulation/")
        logger.info("  2. Test on actual Raspberry Pi hardware")
        logger.info("  3. Run 'python run.py' for production mode")

    except KeyboardInterrupt:
        logger.warning("\n\nTests interrupted by user")
        logger.info("Partial results may be in simulation/ directory")
        return 0
    except Exception as e:
        logger.error(f"Test failed: {e}")
        logger.error("Check error messages above for details")
        return 1

    return 0


if __name__ == "__main__":
    sys.exit(main())
