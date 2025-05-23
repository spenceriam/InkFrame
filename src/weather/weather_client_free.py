#!/usr/bin/env python3
"""
Weather client for InkFrame using OpenWeatherMap free tier.
"""
import os
import sys
import logging
import json
import time
import requests
from datetime import datetime, timedelta

logger = logging.getLogger(__name__)

class WeatherClient:
    """Client for OpenWeatherMap API (Free Tier)"""
    
    def __init__(self, config):
        """Initialize the weather client"""
        self.config = config
        self.cache_file = "config/weather_cache.json"
        self.cache = self._load_cache()
    
    def _load_cache(self):
        """Load the weather cache from disk"""
        try:
            if os.path.exists(self.cache_file):
                with open(self.cache_file, 'r') as f:
                    return json.load(f)
        except Exception as e:
            logger.error(f"Error loading cache: {e}")
        
        return {"last_updated": None, "data": None}
    
    def _save_cache(self):
        """Save the weather cache to disk"""
        try:
            os.makedirs(os.path.dirname(self.cache_file), exist_ok=True)
            with open(self.cache_file, 'w') as f:
                json.dump(self.cache, f, indent=2)
        except Exception as e:
            logger.error(f"Error saving cache: {e}")
    
    def _is_cache_valid(self):
        """Check if the cache is still valid"""
        if not self.cache["last_updated"] or not self.cache["data"]:
            return False
            
        last_updated = datetime.fromisoformat(self.cache["last_updated"])
        cache_expiry = self.config["weather"].get("cache_expiry_minutes", 30)
        
        return (datetime.now() - last_updated) < timedelta(minutes=cache_expiry)
    
    def get_weather(self):
        """Get current weather, using cache if valid"""
        if self._is_cache_valid():
            logger.info("Using cached weather data")
            return self.cache["data"]
        
        logger.info("Fetching fresh weather data")
        weather_data = self._fetch_weather()
        
        if weather_data:
            self.cache["last_updated"] = datetime.now().isoformat()
            self.cache["data"] = weather_data
            self._save_cache()
            
        return weather_data
    
    def _fetch_weather(self):
        """Fetch current weather from OpenWeatherMap free tier"""
        api_key = self.config["weather"].get("api_key", "")
        if not api_key:
            logger.error("No OpenWeatherMap API key configured")
            return None
            
        city = self.config["weather"].get("city", "")
        state = self.config["weather"].get("state", "")
        country = self.config["weather"].get("country", "")
        
        if not city:
            logger.error("No city configured for weather")
            return None
            
        # Build location string
        location_str = city
        if state:
            location_str += f",{state}"
        if country:
            location_str += f",{country}"
            
        units = self.config["weather"].get("units", "metric")
        
        try:
            # Use the free current weather API
            url = "https://api.openweathermap.org/data/2.5/weather"
            params = {
                "q": location_str,
                "appid": api_key,
                "units": units
            }
            
            logger.info(f"Fetching weather for: {location_str}")
            response = requests.get(url, params=params, timeout=10)
            
            if response.status_code != 200:
                logger.error(f"Weather API error: {response.status_code} - {response.text}")
                return None
                
            data = response.json()
            
            # Format the data to match what the display expects
            weather_data = {
                "current": {
                    "temp": round(data["main"]["temp"]),
                    "feels_like": round(data["main"]["feels_like"]),
                    "humidity": data["main"]["humidity"],
                    "wind_speed": data["wind"]["speed"],
                    "weather": [{
                        "main": data["weather"][0]["main"],
                        "description": data["weather"][0]["description"],
                        "icon": data["weather"][0]["icon"]
                    }]
                },
                "location": data["name"],
                "country": data["sys"]["country"],
                "units": units
            }
            
            return weather_data
            
        except Exception as e:
            logger.error(f"Error fetching weather: {e}")
            return None
    
    def format_temperature(self, temp, units="metric"):
        """Format temperature for display"""
        if units == "metric":
            return f"{round(temp)}°C"
        else:
            return f"{round(temp)}°F"
    
    def get_weather_icon(self, icon_code):
        """Map OpenWeatherMap icon codes to emoji or text representations"""
        icon_map = {
            "01d": "☀️", "01n": "🌙",  # clear
            "02d": "⛅", "02n": "☁️",   # few clouds
            "03d": "☁️", "03n": "☁️",   # scattered clouds
            "04d": "☁️", "04n": "☁️",   # broken clouds
            "09d": "🌧️", "09n": "🌧️",  # shower rain
            "10d": "🌦️", "10n": "🌧️",  # rain
            "11d": "⛈️", "11n": "⛈️",   # thunderstorm
            "13d": "❄️", "13n": "❄️",   # snow
            "50d": "🌫️", "50n": "🌫️"   # mist
        }
        return icon_map.get(icon_code, "🌡️")