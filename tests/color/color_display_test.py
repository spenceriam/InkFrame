#!/usr/bin/env python3
"""
Test script for 7.3 inch ACeP 7-color e-ink display
"""
import sys
import os
import time

# Add parent directory to Python path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

print("Starting 7.3 inch color e-ink display test...")

try:
    from waveshare_epd import epd7in3f
    print("Successfully imported 7in3f display driver")
except ImportError as e:
    print(f"Failed to import display driver: {e}")
    sys.exit(1)

print("Creating display object...")
epd = epd7in3f.EPD()
print(f"Display dimensions: {epd.width} x {epd.height}")

print("\nInitializing display...")
print("This may take 10-15 seconds - please wait...")
start_time = time.time()
epd.init()
init_time = time.time() - start_time
print(f"Display initialized successfully! (took {init_time:.1f} seconds)")

print("\nCreating test image with all 7 colors...")
from PIL import Image, ImageDraw, ImageFont

# Create a new image with white background
image = Image.new('RGB', (epd.width, epd.height), (255, 255, 255))
draw = ImageDraw.Draw(image)

# Define the 7 colors supported by the display
colors = [
    ((0, 0, 0), "Black"),
    ((255, 255, 255), "White"),
    ((67, 138, 28), "Green"),
    ((100, 64, 255), "Blue"),
    ((191, 0, 0), "Red"),
    ((255, 243, 56), "Yellow"),
    ((232, 126, 0), "Orange")
]

# Draw color bars
bar_height = epd.height // 7
for i, (color, name) in enumerate(colors):
    y_start = i * bar_height
    y_end = (i + 1) * bar_height
    
    # Draw color bar
    draw.rectangle([(0, y_start), (epd.width - 150, y_end)], fill=color)
    
    # Draw label
    draw.rectangle([(epd.width - 150, y_start), (epd.width, y_end)], fill=(255, 255, 255))
    draw.text((epd.width - 140, y_start + bar_height // 2 - 10), name, fill=(0, 0, 0))

print("\nDisplaying test pattern...")
print("This will take 30-60 seconds for a color display - please be patient...")
start_time = time.time()
epd.display(epd.getbuffer(image))
display_time = time.time() - start_time
print(f"Display updated successfully! (took {display_time:.1f} seconds)")

print("\nTest pattern should now be visible on the display")
print("Waiting 10 seconds before clearing...")
time.sleep(10)

print("\nClearing display...")
start_time = time.time()
epd.Clear()
clear_time = time.time() - start_time
print(f"Display cleared successfully! (took {clear_time:.1f} seconds)")

print("\nPutting display to sleep...")
epd.sleep()
print("Display is now in sleep mode")

print("\nTest completed successfully!")