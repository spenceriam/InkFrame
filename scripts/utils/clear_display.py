#!/usr/bin/env python3
"""
Manual script to clear the e-ink display
"""
import os
import sys
import time
import logging

# Add project root to path for imports
project_root = os.path.abspath(os.path.join(os.path.dirname(__file__), '..', '..'))
sys.path.insert(0, project_root)

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def clear_display_direct():
    """Clear the display using direct driver access"""
    try:
        # Import the specific driver for 7.3" color display
        from waveshare_epd import epd7in3f
        
        logger.info("Using direct driver access to clear display...")
        epd = epd7in3f.EPD()
        
        # Initialize
        logger.info("Initializing display...")
        epd.init()
        
        # Clear - this should turn the display white
        logger.info("Clearing display (this may take ~35 seconds)...")
        epd.Clear()
        
        # Sleep
        logger.info("Putting display to sleep...")
        time.sleep(2)
        epd.sleep()
        
        logger.info("Display cleared successfully!")
        return True
        
    except ImportError:
        logger.error("Waveshare driver not found. Make sure you're running on the Raspberry Pi.")
        return False
    except Exception as e:
        logger.error(f"Error clearing display: {e}")
        return False

def clear_display_wrapper(display_type="7in3f", color_mode="color"):
    """Clear the e-ink display using the wrapper"""
    try:
        from src.display.eink_driver import EInkDisplay
        
        logger.info(f"Initializing {display_type} display in {color_mode} mode...")
        display = EInkDisplay(display_type=display_type, color_mode=color_mode)
        
        if not display.initialized:
            logger.error("Failed to initialize display")
            return False
        
        logger.info("Clearing display...")
        display.clear()
        logger.info("Display cleared successfully!")
        
        # Put display to sleep
        logger.info("Putting display to sleep...")
        display.sleep()
        display.close()
        
        return True
        
    except Exception as e:
        logger.error(f"Error clearing display: {e}")
        return False

if __name__ == "__main__":
    import argparse
    parser = argparse.ArgumentParser(description="Clear the e-ink display")
    parser.add_argument("--display", default="7in3f", help="Display type (default: 7in3f)")
    parser.add_argument("--mode", default="color", help="Color mode (default: color)")
    parser.add_argument("--direct", action="store_true", help="Use direct driver access")
    
    args = parser.parse_args()
    
    if args.direct:
        success = clear_display_direct()
    else:
        success = clear_display_wrapper(args.display, args.mode)
    
    sys.exit(0 if success else 1)