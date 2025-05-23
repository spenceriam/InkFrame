#!/usr/bin/env python3
"""
Debug photo manager settings
"""
from src.display.photo_manager import PhotoManager

pm = PhotoManager()

print("Photo Manager Debug Info:")
print(f"Display type: {pm.display.display_type}")
print(f"Color mode: {pm.display.color_mode}")
print(f"Is color display: {pm.display.is_color_display}")
print(f"Grayscale mode: {pm.display.grayscale_mode}")
print(f"Display size: {pm.display.width}x{pm.display.height}")

print("\nConfig settings:")
print(f"Display type in config: {pm.config['display'].get('type', 'not set')}")
print(f"Color mode in config: {pm.config['display'].get('color_mode', 'not set')}")