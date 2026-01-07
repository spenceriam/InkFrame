#!/usr/bin/env python3
"""
Clear weather cache to force fresh API call
"""
import os
import json

cache_file = ".weather_cache.json"

if os.path.exists(cache_file):
    print(f"Removing weather cache: {cache_file}")
    os.remove(cache_file)
    print("Weather cache cleared!")
else:
    print("No weather cache found")

# Also check if config has API key
config_path = "config/config.json"
if os.path.exists(config_path):
    with open(config_path, 'r') as f:
        config = json.load(f)
    
    weather = config.get('weather', {})
    api_key = weather.get('api_key', '')
    city = weather.get('city', '')
    
    print("\nWeather configuration:")
    print(f"  API key: {'SET' if api_key else 'NOT SET - Run python3 set_weather_config.py'}")
    print(f"  Location: {city if city else 'NOT SET'}")
    
    if not api_key:
        print("\nYou need to set your OpenWeatherMap API key!")
        print("Run: python3 set_weather_config.py")