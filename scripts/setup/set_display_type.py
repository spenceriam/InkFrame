#!/usr/bin/env python3
"""
Script to set the display type for InkFrame
"""
import os
import json

config_path = "config/config.json"
default_config_path = "config/default_config.json"

# Load existing config or create from default
if os.path.exists(config_path):
    with open(config_path, 'r') as f:
        config = json.load(f)
else:
    with open(default_config_path, 'r') as f:
        config = json.load(f)

print("\n=== InkFrame Display Configuration ===\n")
print("Available display types:")
print("1. 7in5_V2 - 7.5 inch Black & White V2 (800×480)")
print("2. 7in3f   - 7.3 inch ACeP 7-color (800×480)")

choice = input("\nSelect display type (1 or 2): ").strip()

if choice == "1":
    config['display']['type'] = "7in5_V2"
    config['display']['color_mode'] = "grayscale"
    print("\nConfigured for 7.5 inch B&W display")
elif choice == "2":
    config['display']['type'] = "7in3f"
    config['display']['color_mode'] = "color"
    print("\nConfigured for 7.3 inch color display")
else:
    print("\nInvalid choice, keeping current configuration")
    exit(1)

# Save config
os.makedirs(os.path.dirname(config_path), exist_ok=True)
with open(config_path, 'w') as f:
    json.dump(config, f, indent=2)

print(f"\nConfiguration saved to {config_path}")
print(f"Display type: {config['display']['type']}")
print(f"Color mode: {config['display']['color_mode']}")