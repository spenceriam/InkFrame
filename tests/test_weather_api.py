#!/usr/bin/env python3
"""
Test OpenWeatherMap API key and endpoints
"""
import json
import requests
import sys

# Load config
try:
    with open('config/config.json', 'r') as f:
        config = json.load(f)
except FileNotFoundError:
    print("Error: config/config.json not found. Run set_weather_config.py first.")
    sys.exit(1)

api_key = config['weather']['api_key']
city = config['weather']['city']
state = config['weather']['state']
country = config['weather']['country']
units = config['weather']['units']

if not api_key:
    print("Error: No API key found in config")
    sys.exit(1)

print(f"\n=== Testing OpenWeatherMap API ===")
print(f"API Key: {'*' * 8 + api_key[-4:]}")
print(f"Location: {city}, {state}, {country}")
print(f"Units: {units}\n")

# Test 1: Current Weather API (free tier)
print("1. Testing Current Weather API (free tier)...")
current_url = "https://api.openweathermap.org/data/2.5/weather"
location_str = f"{city},{state},{country}" if state else f"{city},{country}"
params = {
    "q": location_str,
    "appid": api_key,
    "units": units
}

try:
    response = requests.get(current_url, params=params, timeout=10)
    print(f"   Status: {response.status_code}")
    if response.status_code == 200:
        data = response.json()
        print(f"   ✓ Success! Temperature: {data['main']['temp']}°")
        print(f"   Weather: {data['weather'][0]['description']}")
        print(f"   Location confirmed: {data['name']}, {data['sys']['country']}")
    else:
        print(f"   ✗ Error: {response.text}")
except Exception as e:
    print(f"   ✗ Exception: {e}")

# Test 2: OneCall API (requires subscription)
print("\n2. Testing OneCall API (requires subscription)...")
# First get coordinates
if response.status_code == 200:
    lat = data['coord']['lat']
    lon = data['coord']['lon']
    
    onecall_url = "https://api.openweathermap.org/data/2.5/onecall"
    params = {
        "lat": lat,
        "lon": lon,
        "appid": api_key,
        "units": units,
        "exclude": "minutely,hourly"
    }
    
    try:
        response = requests.get(onecall_url, params=params, timeout=10)
        print(f"   Status: {response.status_code}")
        if response.status_code == 200:
            print(f"   ✓ OneCall API is active on your key!")
        else:
            print(f"   ✗ OneCall API not available: {response.text}")
            print(f"   Note: OneCall API requires a subscription. Using free tier is recommended.")
    except Exception as e:
        print(f"   ✗ Exception: {e}")

# Test 3: Geocoding API (free tier)
print("\n3. Testing Geocoding API (free tier)...")
geo_url = "http://api.openweathermap.org/geo/1.0/direct"
geo_params = {
    "q": location_str,
    "limit": 1,
    "appid": api_key
}

try:
    response = requests.get(geo_url, params=geo_params, timeout=10)
    print(f"   Status: {response.status_code}")
    if response.status_code == 200 and response.json():
        geo_data = response.json()[0]
        print(f"   ✓ Location found: {geo_data['name']}, {geo_data.get('state', '')}, {geo_data['country']}")
        print(f"   Coordinates: {geo_data['lat']}, {geo_data['lon']}")
    else:
        print(f"   ✗ Error: {response.text}")
except Exception as e:
    print(f"   ✗ Exception: {e}")

print("\n=== Test Complete ===")
print("\nRecommendation: If OneCall API fails with 401, the weather client should be")
print("updated to use the free Current Weather API instead.")