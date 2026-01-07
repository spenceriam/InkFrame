#!/usr/bin/env python3
"""
Weather client for InkFrame using weather.gov API.
Based on EazyWeather weather service patterns.
"""

import json
import logging
import os
import sys
import time
from datetime import datetime
from typing import Any, Dict, Optional, Tuple

import requests

logger = logging.getLogger(__name__)


class WeatherClient:
    """Client for National Weather Service API (weather.gov)"""

    def __init__(self, config):
        """Initialize the weather client

        Args:
            config: Configuration dictionary
        """
        self.config = config
        self.cache_file = "config/weather_cache.json"
        self.cache = self._load_cache()

        # Weather.gov API configuration
        self.base_url = "https://api.weather.gov"
        self.user_agent = "(InkFrame, inkframe@example.com)"

        # Location configuration
        self._coordinates = None
        self._grid_info = None

        # Default fallback coordinates (McHenry, IL)
        self.default_lat = 42.3333
        self.default_lon = -88.6167

        # Rate limiting configuration
        self.min_request_interval = 30  # 30 seconds between requests
        self.last_request_time = 0

    def _load_cache(self):
        """Load the weather cache from disk"""
        try:
            if os.path.exists(self.cache_file):
                with open(self.cache_file, "r") as f:
                    return json.load(f)
        except Exception as e:
            logger.error(f"Error loading cache: {e}")

        return {"last_updated": None, "data": None}

    def _save_cache(self):
        """Save the weather cache to disk"""
        try:
            os.makedirs(os.path.dirname(self.cache_file), exist_ok=True)
            with open(self.cache_file, "w") as f:
                json.dump(self.cache, f, indent=2)
        except Exception as e:
            logger.error(f"Error saving cache: {e}")

    def _is_cache_valid(self):
        """Check if the cache is still valid"""
        if not self.cache["last_updated"] or not self.cache["data"]:
            return False

        try:
            last_updated = datetime.fromisoformat(self.cache["last_updated"])
            cache_expiry = self.config["weather"].get("cache_expiry_minutes", 30)
            return (datetime.now() - last_updated).total_seconds() < (cache_expiry * 60)
        except:
            return False

    def _rate_limit(self):
        """Implement rate limiting for API calls"""
        now = time.time()
        time_since_last = now - self.last_request_time

        if time_since_last < self.min_request_interval:
            wait_time = self.min_request_interval - time_since_last
            logger.debug(f"Rate limiting: waiting {wait_time:.1f} seconds")
            time.sleep(wait_time)

        self.last_request_time = time.time()

    def _fetch_with_user_agent(self, url: str, headers: Dict[str, str] = None) -> Any:
        """Make HTTP request with proper User-Agent header

        Args:
            url: URL to fetch
            headers: Additional headers

        Returns:
            Parsed JSON response
        """
        self._rate_limit()

        default_headers = {
            "User-Agent": self.user_agent,
            "Accept": "application/geo+json",
        }

        if headers:
            default_headers.update(headers)

        try:
            response = requests.get(url, headers=default_headers, timeout=10)

            if response.status_code == 429:
                logger.warning("Rate limit hit, retrying after delay")
                time.sleep(5)
                response = requests.get(url, headers=default_headers, timeout=10)

            response.raise_for_status()
            return response.json()
        except Exception as e:
            logger.error(f"API request failed for {url}: {e}")
            raise

    def _get_coordinates_from_config(self) -> Optional[Tuple[float, float]]:
        """Get coordinates from configuration if available

        Returns:
            Tuple of (latitude, longitude) or None
        """
        try:
            city = self.config["weather"].get("city", "")
            state = self.config["weather"].get("state", "")

            if city:
                # Try geocoding the city/state
                search_query = f"{city}, {state}" if state else city

                try:
                    url = f"https://nominatim.openstreetmap.org/search"
                    params = {
                        "q": search_query,
                        "format": "json",
                        "limit": 1,
                        "addressdetails": 1,
                    }

                    response = requests.get(
                        url,
                        params=params,
                        headers={"User-Agent": self.user_agent},
                        timeout=10,
                    )

                    if response.status_code == 200 and response.json():
                        result = response.json()[0]
                        lat = float(result["lat"])
                        lon = float(result["lon"])
                        logger.info(f"Coordinates from config: {lat}, {lon}")
                        return (lat, lon)
                except Exception as e:
                    logger.warning(f"Geocoding failed for {search_query}: {e}")

        except Exception as e:
            logger.warning(f"Error getting coordinates from config: {e}")

        return None

    def _get_coordinates_from_ip(self) -> Optional[Tuple[float, float]]:
        """Get coordinates via IP geolocation

        Returns:
            Tuple of (latitude, longitude) or None
        """
        try:
            # Try ip-api.com (free, no API key required)
            response = requests.get("http://ip-api.com/json/", timeout=5)

            if response.status_code == 200:
                data = response.json()
                if data.get("status") == "success":
                    lat = data.get("lat")
                    lon = data.get("lon")
                    if lat is not None and lon is not None:
                        logger.info(f"Coordinates from IP: {lat}, {lon}")
                        return (lat, lon)
        except Exception as e:
            logger.warning(f"IP geolocation failed: {e}")

        return None

    def _get_coordinates(self) -> Tuple[float, float]:
        """Get coordinates using multiple strategies

        Returns:
            Tuple of (latitude, longitude)
        """
        if self._coordinates:
            return self._coordinates

        # Try config first
        coords = self._get_coordinates_from_config()
        if coords:
            self._coordinates = coords
            return coords

        # Try IP geolocation
        coords = self._get_coordinates_from_ip()
        if coords:
            self._coordinates = coords
            return coords

        # Fall back to default (McHenry, IL)
        logger.info(
            f"Using default coordinates: {self.default_lat}, {self.default_lon}"
        )
        self._coordinates = (self.default_lat, self.default_lon)
        return self._coordinates

    def _get_grid_info(self) -> Dict:
        """Get NWS grid information for coordinates

        Returns:
            Dictionary containing grid information
        """
        if self._grid_info:
            return self._grid_info

        lat, lon = self._get_coordinates()

        try:
            url = f"{self.base_url}/points/{lat:.4f},{lon:.4f}"
            logger.info(f"Fetching grid info from: {url}")
            point_data = self._fetch_with_user_agent(url)

            self._grid_info = {
                "wfo": point_data["properties"]["cwa"],
                "x": point_data["properties"]["gridX"],
                "y": point_data["properties"]["gridY"],
                "forecast_url": point_data["properties"]["forecast"],
                "forecast_hourly_url": point_data["properties"]["forecastHourly"],
                "stations_url": point_data["properties"]["observationStations"],
            }

            logger.info(
                f"Grid: {self._grid_info['wfo']}, {self._grid_info['x']}, {self._grid_info['y']}"
            )
            return self._grid_info

        except Exception as e:
            logger.error(f"Failed to get grid info: {e}")
            raise

    def _get_current_date(self) -> str:
        """Get current date in "Month Day, Year" format

        Returns:
            Formatted date string
        """
        return datetime.now().strftime("%B %d, %Y")

    def _get_current_conditions(self) -> Optional[Dict]:
        """Get current weather conditions from nearby stations

        Returns:
            Dictionary with current conditions
        """
        try:
            grid_info = self._get_grid_info()

            # Get stations
            stations_data = self._fetch_with_user_agent(grid_info["stations_url"])

            if not stations_data.get("features"):
                logger.warning("No observation stations found")
                return None

            # Get the first station
            station_id = stations_data["features"][0]["properties"]["stationIdentifier"]

            # Get latest observation
            obs_url = f"{self.base_url}/stations/{station_id}/observations/latest"
            obs_data = self._fetch_with_user_agent(obs_url)

            props = obs_data["properties"]

            # Extract temperature
            temp_c = props.get("temperature", {}).get("value")
            temp_f = None
            if temp_c is not None:
                temp_f = round(temp_c * 9 / 5 + 32)  # Convert C to F

            # Extract other data
            humidity = props.get("relativeHumidity", {}).get("value")
            wind_speed_mps = props.get("windSpeed", {}).get("value")
            wind_speed_mph = round(wind_speed_mps * 2.237) if wind_speed_mps else None
            wind_dir = props.get("windDirection", {}).get("value")
            text_description = props.get("textDescription")
            icon = props.get("icon")

            return {
                "temp": temp_f,
                "temp_c": temp_c,
                "condition": text_description or "Unknown",
                "humidity": int(humidity) if humidity else None,
                "wind_speed": wind_speed_mph,
                "wind_direction": wind_dir,
                "icon": icon,
            }

        except Exception as e:
            logger.error(f"Failed to get current conditions: {e}")
            return None

    def _get_forecast(self) -> Optional[Dict]:
        """Get daily forecast

        Returns:
            Dictionary with forecast data
        """
        try:
            grid_info = self._get_grid_info()

            forecast_data = self._fetch_with_user_agent(grid_info["forecast_url"])
            periods = forecast_data["properties"]["periods"]

            if not periods:
                return None

            # Get first period (current or today)
            today = periods[0]

            return {
                "temp": today.get("temperature"),
                "condition": today.get("shortForecast"),
                "detailed": today.get("detailedForecast"),
                "icon": today.get("icon"),
                "is_daytime": today.get("isDaytime", True),
            }

        except Exception as e:
            logger.error(f"Failed to get forecast: {e}")
            return None

    def _fetch_weather(self) -> Optional[Dict]:
        """Fetch weather data from weather.gov

        Returns:
            Dictionary containing weather information
        """
        try:
            # Try to get current conditions first
            current = self._get_current_conditions()

            # Fall back to forecast if current conditions unavailable
            if not current:
                logger.info("Current conditions unavailable, using forecast")
                forecast = self._get_forecast()
                if forecast:
                    current = {
                        "temp": forecast.get("temp"),
                        "condition": forecast.get("condition"),
                        "icon": forecast.get("icon"),
                    }

            if not current:
                return None

            # Get current date
            current_date = self._get_current_date()

            # Format for backward compatibility
            weather_data = {
                "current": {
                    "temp": current.get("temp", "N/A"),
                    "condition": current.get("condition", "Unknown"),
                    "description": current.get("condition", "Unknown"),
                    "humidity": current.get("humidity", "N/A"),
                    "wind_speed": current.get("wind_speed", "N/A"),
                    "feels_like": "N/A",  # NWS doesn't provide this directly
                    "icon": current.get("icon", ""),
                },
                "date": current_date,
                "has_alert": False,
                "raw_data": current,
            }

            return weather_data

        except Exception as e:
            logger.error(f"Error fetching weather: {e}")
            return None

    def get_weather(self):
        """Get current weather, using cache if valid

        Returns:
            Dictionary with weather information or None
        """
        if self._is_cache_valid():
            logger.info("Using cached weather data")
            weather_data = self.cache["data"]
        else:
            logger.info("Fetching fresh weather data")
            weather_data = self._fetch_weather()

            if weather_data:
                self.cache["last_updated"] = datetime.now().isoformat()
                self.cache["data"] = weather_data
                self._save_cache()

        return weather_data

    def format_temperature(self, temp, units="metric"):
        """Format temperature with appropriate unit symbol

        Args:
            temp: Temperature value
            units: 'metric' or 'imperial'

        Returns:
            Formatted temperature string
        """
        if temp is None or temp == "N/A":
            return "N/A"

        unit_symbol = "°C" if units == "metric" else "°F"

        # weather.gov provides Fahrenheit directly
        return f"{round(temp)}{unit_symbol}"
