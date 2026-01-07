#!/usr/bin/env python3
"""
Debug Waveshare EPD import issues
"""
import sys
import os
import importlib

print("=== Waveshare EPD Debug ===\n")

print("1. Python executable:")
print(f"   {sys.executable}")

print("\n2. Python path:")
for i, path in enumerate(sys.path):
    print(f"   [{i}] {path}")

print("\n3. Checking for waveshare_epd directory:")
# Check common locations
locations = [
    os.path.join(os.getcwd(), "waveshare_epd"),
    os.path.join(os.path.dirname(__file__), "waveshare_epd"),
    "/home/spencer/InkFrame/waveshare_epd",
]

for loc in locations:
    if os.path.exists(loc):
        print(f"   ✓ Found: {loc}")
        files = os.listdir(loc)
        print(f"     Files: {len(files)} items")
        if "epd7in5_V2.py" in files:
            print("     ✓ epd7in5_V2.py exists")
        if "__init__.py" in files:
            print("     ✓ __init__.py exists")
    else:
        print(f"   ✗ Not found: {loc}")

print("\n4. Trying direct import:")
try:
    import waveshare_epd
    print("   ✓ Successfully imported waveshare_epd")
    print(f"   Module location: {waveshare_epd.__file__}")
except ImportError as e:
    print(f"   ✗ Failed to import waveshare_epd: {e}")

print("\n5. Trying module import:")
try:
    module = importlib.import_module("waveshare_epd.epd7in5_V2")
    print("   ✓ Successfully imported waveshare_epd.epd7in5_V2")
except ImportError as e:
    print(f"   ✗ Failed to import: {e}")

print("\n6. Adding current directory to path and retrying:")
sys.path.insert(0, os.getcwd())
try:
    import waveshare_epd.epd7in5_V2
    print("   ✓ Success after adding current directory to path!")
except ImportError as e:
    print(f"   ✗ Still failed: {e}")

print("\n7. Checking if running from correct directory:")
print(f"   Current working directory: {os.getcwd()}")
print(f"   Script directory: {os.path.dirname(os.path.abspath(__file__))}")

print("\n=== Recommendation ===")
print("The service needs to run from the InkFrame directory or")
print("the PYTHONPATH needs to include the InkFrame directory.")