#!/usr/bin/env python3
"""
Script to set OpenWeatherMap API key and location for InkFrame
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

print("\n=== InkFrame Weather Configuration ===\n")

# Get API key
api_key = input("Enter your OpenWeatherMap API key: ").strip()
if api_key:
    config['weather']['api_key'] = api_key

# Get location
city = input("Enter your city (e.g., Austin): ").strip()
if city:
    config['weather']['city'] = city

state = input("Enter your state/province code (e.g., TX): ").strip()
if state:
    config['weather']['state'] = state

country = input("Enter your country code (e.g., US): ").strip()
if country:
    config['weather']['country'] = country

# Ask for units preference
units = input("Temperature units - metric (°C) or imperial (°F)? [metric]: ").strip().lower()
if units in ['metric', 'imperial']:
    config['weather']['units'] = units
elif not units:
    config['weather']['units'] = 'metric'

# Save config
os.makedirs(os.path.dirname(config_path), exist_ok=True)
with open(config_path, 'w') as f:
    json.dump(config, f, indent=2)

print(f"\nConfiguration saved to {config_path}")
print("\nWeather configuration:")
print(f"  API Key: {'*' * 8 + api_key[-4:] if api_key else '(not set)'}")
print(f"  Location: {city}, {state}, {country}")
print(f"  Units: {config['weather']['units']}")