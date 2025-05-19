#!/usr/bin/env python3
"""
Weather client for InkFrame.
Handles fetching and caching weather data from OpenWeatherMap.

Features:
- Fetches current weather conditions from OpenWeatherMap API
- Provides forecast data for upcoming days
- Implements intelligent caching to reduce API calls
- Handles API errors gracefully with fallback to cached data
- Supports both metric and imperial units
- Provides weather alerts and warnings when available
"""
import os
import sys
import logging
import json
import time
import requests
import math
from datetime import datetime, timedelta

logger = logging.getLogger(__name__)

class WeatherClient:
    """Client for OpenWeatherMap API
    
    This class handles communication with the OpenWeatherMap API,
    providing current weather data and forecasts with intelligent caching
    to minimize API calls and handle offline scenarios gracefully.
    """
    
    def __init__(self, config):
        """Initialize the weather client
        
        Args:
            config (dict): Application configuration dictionary
        """
        self.config = config
        self.cache_file = "config/weather_cache.json"
        self.cache = self._load_cache()
        
        # Record API call counts to stay within rate limits
        self.daily_api_calls = 0
        self.last_api_call_date = None
    
    def _load_cache(self):
        """Load the weather cache from disk"""
        try:
            if os.path.exists(self.cache_file):
                with open(self.cache_file, 'r') as f:
                    cache = json.load(f)
                logger.info("Loaded weather cache")
                return cache
            else:
                logger.info("No weather cache found, creating new cache")
                return {"last_updated": None, "data": None}
        except Exception as e:
            logger.error(f"Error loading weather cache: {e}")
            return {"last_updated": None, "data": None}
    
    def _save_cache(self):
        """Save the weather cache to disk"""
        try:
            # Ensure directory exists
            os.makedirs(os.path.dirname(self.cache_file), exist_ok=True)
            
            with open(self.cache_file, 'w') as f:
                json.dump(self.cache, f)
            logger.info("Saved weather cache")
        except Exception as e:
            logger.error(f"Error saving weather cache: {e}")
            
    def _track_api_call(self):
        """Track API calls to respect rate limits
        
        Returns:
            bool: True if API call should proceed, False if we've hit limits
        """
        today = datetime.now().date().isoformat()
        
        # Reset counter if it's a new day
        if self.last_api_call_date != today:
            self.daily_api_calls = 0
            self.last_api_call_date = today
        
        # Check if we're within limits (free tier is 1000 calls per day)
        max_daily_calls = self.config["weather"].get("max_daily_api_calls", 950)  # Default slightly under limit
        
        if self.daily_api_calls >= max_daily_calls:
            logger.warning(f"Daily API call limit reached ({max_daily_calls}), using cached data")
            return False
        
        # Increment counter and proceed
        self.daily_api_calls += 1
        return True
    
    def _format_wind_direction(self, degrees):
        """Convert wind direction in degrees to cardinal direction
        
        Args:
            degrees (float): Wind direction in degrees
            
        Returns:
            str: Cardinal direction abbreviation (N, NE, E, etc.)
        """
        directions = ["N", "NNE", "NE", "ENE", "E", "ESE", "SE", "SSE", 
                     "S", "SSW", "SW", "WSW", "W", "WNW", "NW", "NNW"]
        
        # Convert degrees to a directions index (0-15)
        index = round(degrees / 22.5) % 16
        return directions[index]
    
    def _is_cache_valid(self):
        """Check if the cache is still valid"""
        if not self.cache["last_updated"] or not self.cache["data"]:
            return False
            
        # Convert string timestamp to datetime
        last_updated = datetime.fromisoformat(self.cache["last_updated"])
        
        # Get cache expiry in minutes
        cache_expiry = self.config["weather"].get("cache_expiry_minutes", 120)
        
        # Check if cache has expired
        expiry_time = last_updated + timedelta(minutes=cache_expiry)
        return datetime.now() < expiry_time
    
    def fetch_weather(self):
        """Fetch current weather from OpenWeatherMap
        
        Returns:
            dict: Weather data dictionary, or None if unsuccessful
        """
        # Check if we should make an API call
        if not self._track_api_call():
            return self.cache.get("data")
        
        api_key = self.config["weather"].get("api_key", "")
        if not api_key:
            logger.error("No OpenWeatherMap API key configured")
            return None
            
        # Get location information from config
        city = self.config["weather"].get("city", "")
        state = self.config["weather"].get("state", "")
        country = self.config["weather"].get("country", "")
        lat = self.config["weather"].get("latitude")
        lon = self.config["weather"].get("longitude")
        
        # Check if we have coordinates or city
        if lat is not None and lon is not None:
            location_type = "coords"
            location_str = f"{lat},{lon}"
        elif city:
            location_type = "city"
            # Format location string
            location_str = city
            if state:
                location_str += f",{state}"
            if country:
                location_str += f",{country}"
        else:
            logger.error("No location configured for weather (need city or lat/lon)")
            return None
            
        units = self.config["weather"].get("units", "metric")
        lang = self.config["weather"].get("language", "en")
        
        try:
            # Use OneCall API for more complete data in a single call
            url = f"https://api.openweathermap.org/data/2.5/onecall"
            
            if location_type == "coords":
                params = {
                    "lat": lat,
                    "lon": lon,
                    "appid": api_key,
                    "units": units,
                    "lang": lang,
                    "exclude": "minutely,hourly"  # Exclude data we don't need
                }
                logger.info(f"Fetching weather for coordinates: {lat},{lon}")
            else:
                # Use geocoding API to get coordinates from city name first
                geo_url = "http://api.openweathermap.org/geo/1.0/direct"
                geo_params = {
                    "q": location_str,
                    "limit": 1,
                    "appid": api_key
                }
                
                logger.info(f"Geocoding location: {location_str}")
                geo_response = requests.get(geo_url, params=geo_params, timeout=10)
                
                if geo_response.status_code != 200 or not geo_response.json():
                    logger.error(f"Geocoding error: {geo_response.status_code} - {geo_response.text}")
                    return None
                
                geo_data = geo_response.json()[0]
                lat, lon = geo_data["lat"], geo_data["lon"]
                
                params = {
                    "lat": lat,
                    "lon": lon,
                    "appid": api_key,
                    "units": units,
                    "lang": lang,
                    "exclude": "minutely,hourly"  # Exclude data we don't need
                }
                logger.info(f"Fetching weather for {location_str} at {lat},{lon}")
            
            # Make the API call
            response = requests.get(url, params=params, timeout=10)
            
            if response.status_code != 200:
                logger.error(f"Weather API error: {response.status_code} - {response.text}")
                return None
                
            data = response.json()
            
            # Extract current weather data
            current = data["current"]
            weather = current["weather"][0]
            
            # Format wind direction
            wind_direction = ""
            if "wind_deg" in current:
                wind_direction = self._format_wind_direction(current["wind_deg"])
            
            # Create a more structured and complete weather data object
            weather_data = {
                "temp": round(current["temp"]),
                "feels_like": round(current["feels_like"]),
                "temp_min": round(data["daily"][0]["temp"]["min"]) if "daily" in data else None,
                "temp_max": round(data["daily"][0]["temp"]["max"]) if "daily" in data else None,
                "condition": weather["main"],
                "description": weather["description"],
                "humidity": current["humidity"],
                "pressure": current["pressure"],
                "wind_speed": current["wind_speed"],
                "wind_direction": wind_direction,
                "clouds": current.get("clouds", 0),
                "uv_index": current.get("uvi", 0),
                "visibility": current.get("visibility", 0),
                "icon": weather["icon"],
                "rain_1h": current.get("rain", {}).get("1h", 0) if "rain" in current else 0,
                "snow_1h": current.get("snow", {}).get("1h", 0) if "snow" in current else 0,
                "sunrise": current["sunrise"],
                "sunset": current["sunset"],
                "timezone": data["timezone"],
                "location": location_str,
                "latitude": lat,
                "longitude": lon,
            }
            
            # Add daily forecast data
            if "daily" in data:
                forecast = []
                for i, day in enumerate(data["daily"][:5]):  # Get 5-day forecast
                    if i == 0:  # Skip today as we already have current conditions
                        continue
                        
                    # Get day name
                    timestamp = day["dt"]
                    day_name = datetime.fromtimestamp(timestamp).strftime("%a")
                    
                    forecast.append({
                        "day": day_name,
                        "temp": round((day["temp"]["max"] + day["temp"]["min"]) / 2),  # Average temp
                        "temp_min": round(day["temp"]["min"]),
                        "temp_max": round(day["temp"]["max"]),
                        "condition": day["weather"][0]["main"],
                        "icon": day["weather"][0]["icon"],
                        "precipitation": round(day.get("pop", 0) * 100)  # Probability of precipitation as %
                    })
                
                weather_data["forecast"] = forecast
            
            # Check for weather alerts
            has_alert = False
            alert_messages = []
            if "alerts" in data:
                has_alert = True
                for alert in data["alerts"]:
                    alert_messages.append({
                        "sender": alert.get("sender_name", "Weather Service"),
                        "event": alert.get("event", "Alert"),
                        "description": alert.get("description", ""),
                        "start": alert.get("start", 0),
                        "end": alert.get("end", 0)
                    })
            
            weather_data["has_alert"] = has_alert
            weather_data["alerts"] = alert_messages
            
            # Update cache with the new data
            self.cache["data"] = weather_data
            self.cache["last_updated"] = datetime.now().isoformat()
            self._save_cache()
            
            logger.info(f"Weather updated: {weather_data['temp']}° {weather_data['condition']}")
            return weather_data
            
        except requests.RequestException as e:
            logger.error(f"Error fetching weather: {e}")
            # Fall back to cached data if available
            if self.cache.get("data"):
                logger.info("Using cached data due to API error")
                return self.cache["data"]
            return None
        except (KeyError, ValueError, TypeError, IndexError) as e:
            logger.error(f"Error parsing weather data: {e}")
            # Fall back to cached data if available
            if self.cache.get("data"):
                logger.info("Using cached data due to parsing error")
                return self.cache["data"]
            return None
    
    def get_current_weather(self, force_refresh=False):
        """Get current weather, using cache if valid
        
        Args:
            force_refresh (bool): Whether to force a refresh regardless of cache validity
            
        Returns:
            dict: Weather data dictionary, or None if unsuccessful
        """
        if not force_refresh and self._is_cache_valid():
            logger.info("Using cached weather data")
            return self.cache["data"]
        else:
            logger.info("Fetching fresh weather data")
            return self.fetch_weather()
    
    def get_forecast(self, days=5):
        """Get weather forecast for upcoming days
        
        Args:
            days (int): Number of days to get forecast for (1-5)
            
        Returns:
            list: List of forecast data dictionaries, or None if unsuccessful
        """
        # Get weather data which includes forecast
        weather_data = self.get_current_weather()
        
        if not weather_data or "forecast" not in weather_data:
            return None
            
        # Limit forecast to requested number of days
        return weather_data["forecast"][:min(days, len(weather_data["forecast"]))]
    
    def get_weather_alerts(self):
        """Get any active weather alerts or warnings
        
        Returns:
            list: List of alert dictionaries, or None if no alerts
        """
        weather_data = self.get_current_weather()
        
        if not weather_data or not weather_data.get("has_alert", False):
            return None
            
        return weather_data.get("alerts", [])
    
    def get_sun_times(self):
        """Get sunrise and sunset times
        
        Returns:
            dict: Dictionary with sunrise and sunset timestamps, or None if unavailable
        """
        weather_data = self.get_current_weather()
        
        if not weather_data or "sunrise" not in weather_data or "sunset" not in weather_data:
            return None
            
        # Convert timestamps to datetime objects in local timezone
        timezone_offset = weather_data.get("timezone_offset", 0)
        
        sunrise = datetime.fromtimestamp(weather_data["sunrise"])
        sunset = datetime.fromtimestamp(weather_data["sunset"])
        
        return {
            "sunrise": sunrise,
            "sunset": sunset,
            "daylight_hours": (sunset - sunrise).seconds / 3600  # Hours of daylight
        }
    
if __name__ == "__main__":
    # Simple test when run directly
    logging.basicConfig(level=logging.INFO)
    
    # Load config
    try:
        with open("config/default_config.json", 'r') as f:
            config = json.load(f)
    except Exception:
        # Minimal test config
        config = {
            "weather": {
                "api_key": "",
                "city": "London",
                "country": "UK",
                "units": "metric",
                "cache_expiry_minutes": 60,
                "max_daily_api_calls": 950,
                "language": "en"
            }
        }
    
    # Parse command line arguments
    import argparse
    parser = argparse.ArgumentParser(description="Weather client for InkFrame")
    parser.add_argument("--refresh", action="store_true", help="Force refresh weather data")
    parser.add_argument("--forecast", action="store_true", help="Show forecast data")
    parser.add_argument("--alerts", action="store_true", help="Show weather alerts")
    parser.add_argument("--sun", action="store_true", help="Show sunrise/sunset times")
    parser.add_argument("--all", action="store_true", help="Show all weather data")
    
    args = parser.parse_args()
    
    # Initialize client
    client = WeatherClient(config)
    
    # Check if API key is configured
    if not config["weather"]["api_key"]:
        print("No OpenWeatherMap API key configured in config/default_config.json")
        print("Get a free API key at https://openweathermap.org/api")
        sys.exit(1)
    
    # Get weather data
    force_refresh = args.refresh or args.all
    weather = client.get_current_weather(force_refresh=force_refresh)
    
    if not weather:
        print("No weather data available")
        sys.exit(1)
    
    # Print current weather
    location = weather.get("location", "Unknown")
    temp = weather.get("temp", "N/A")
    condition = weather.get("condition", "Unknown")
    description = weather.get("description", "")
    
    units = config["weather"].get("units", "metric")
    unit_symbol = "°C" if units == "metric" else "°F"
    
    print(f"\nCurrent Weather for {location}:")
    print(f"Temperature: {temp}{unit_symbol} (feels like {weather.get('feels_like', 'N/A')}{unit_symbol})")
    print(f"Condition: {condition} - {description}")
    print(f"Humidity: {weather.get('humidity', 'N/A')}%")
    print(f"Wind: {weather.get('wind_speed', 'N/A')} {weather.get('wind_direction', '')}")
    
    # Print forecast if requested
    if args.forecast or args.all:
        forecast = weather.get("forecast")
        if forecast:
            print("\nForecast:")
            for day in forecast:
                print(f"  {day['day']}: {day['temp']}{unit_symbol} ({day['condition']}) - {day['precipitation']}% chance of precipitation")
    
    # Print alerts if requested
    if (args.alerts or args.all) and weather.get("has_alert", False):
        alerts = weather.get("alerts", [])
        if alerts:
            print("\nWeather Alerts:")
            for alert in alerts:
                print(f"  {alert['event']} from {alert['sender']}")
                start_time = datetime.fromtimestamp(alert['start']).strftime("%Y-%m-%d %H:%M")
                end_time = datetime.fromtimestamp(alert['end']).strftime("%Y-%m-%d %H:%M")
                print(f"    From {start_time} to {end_time}")
                print(f"    {alert['description'][:100]}..." if len(alert['description']) > 100 else f"    {alert['description']}")
    
    # Print sun times if requested
    if args.sun or args.all:
        sun_times = client.get_sun_times()
        if sun_times:
            print("\nSun Times:")
            print(f"  Sunrise: {sun_times['sunrise'].strftime('%H:%M')}")
            print(f"  Sunset: {sun_times['sunset'].strftime('%H:%M')}")
            print(f"  Daylight: {sun_times['daylight_hours']:.1f} hours")
    
    print("\nLast Updated: {}".format(
        datetime.fromisoformat(client.cache["last_updated"]).strftime("%Y-%m-%d %H:%M:%S")
        if client.cache["last_updated"] else "Never"
    ))
    
    # Cache info
    cache_valid = client._is_cache_valid()
    cache_expiry = config["weather"].get("cache_expiry_minutes", 60)
    print(f"Cache Status: {'Valid' if cache_valid else 'Expired'} (expires after {cache_expiry} minutes)")
    
    # Suggest next steps if this is the first run
    if weather.get("has_alert", False) and not (args.alerts or args.all):
        print("\nNOTE: Weather alerts are active! Use --alerts to see details.")
    
    print("\nFor more options, use --help")
    print("Example: python weather_client.py --all")