#!/usr/bin/env python3
"""
Test the photo manager display directly
"""
import logging
from src.display.photo_manager import PhotoManager

logging.basicConfig(level=logging.DEBUG)

print("Testing photo manager...")

try:
    # Create photo manager
    pm = PhotoManager()
    
    print("Photo manager initialized")
    print(f"Display size: {pm.display.width}x{pm.display.height}")
    print(f"Status bar height: {pm.config['display']['status_bar_height']}")
    
    # Try to display a photo
    print("\nDisplaying a photo...")
    result = pm.display_photo(force_refresh=True)
    
    if result:
        print("Photo displayed successfully!")
    else:
        print("Failed to display photo!")
        
except Exception as e:
    print(f"Error: {e}")
    import traceback
    traceback.print_exc()