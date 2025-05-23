#!/usr/bin/env python3
"""
Photo manager for InkFrame.
Handles photo selection, rotation, and display coordination.

Features:
- Intelligent photo selection to avoid repetition
- Status bar with time, date, and weather information
- Multiple display modes (photo, clock, information)
- Smart refresh patterns to extend e-ink display life
- Support for manual control via external signals
"""
import os
import sys
import logging
import time
import random
import json
import signal
import pytz
from datetime import datetime, timedelta
from PIL import Image, ImageDraw, ImageFont, ImageFilter
from enum import Enum

from src.display.eink_driver import EInkDisplay
from src.weather.weather_client import WeatherClient

logger = logging.getLogger(__name__)

class DisplayMode(Enum):
    """Enum for different display modes"""
    PHOTO = 1      # Show photos with status bar
    CLOCK = 2      # Show large clock with date and weather
    INFO = 3       # Show system information and status
    WEATHER = 4    # Show detailed weather information

class PhotoManager:
    """Manages photo selection and display
    
    This class orchestrates the display of photos and status information
    on the e-ink display, handling rotation timing, layout, and content selection.
    """
    
    def __init__(self, config_path="config/config.json"):
        """Initialize the photo manager
        
        Args:
            config_path (str): Path to configuration file
        """
        self.config = self._load_config(config_path)
        
        # Initialize display with display type and color mode from config
        display_type = self.config["display"].get("display_type", "7in5_V2")
        color_mode = self.config["display"].get("color_mode", "grayscale")
        self.display = EInkDisplay(display_type=display_type, color_mode=color_mode)
        
        self.weather_client = WeatherClient(self.config)
        
        # Initialize tracking of displayed photos
        self.photo_history = []
        self.current_photo = None
        self.last_photo_change = time.time()
        self.current_mode = DisplayMode.PHOTO
        
        # Set up folder to track viewed photos
        self.viewed_photos_file = os.path.join(self.config["photos"].get("directory", "static/images/photos"), ".viewed_photos.json")
        self.load_viewed_photos()
        
        # Register signal handlers for external control
        self._setup_signal_handlers()
        
        # Load fonts
        self._load_fonts()
        
        # Track last weather update
        self.last_weather_update = 0
        
    def _load_config(self, config_path):
        """Load configuration from JSON file"""
        try:
            if not os.path.exists(config_path):
                # Use default config if specific config doesn't exist
                config_path = "config/default_config.json"
            
            with open(config_path, 'r') as f:
                config = json.load(f)
            logger.info(f"Loaded configuration from {config_path}")
            return config
        except Exception as e:
            logger.error(f"Error loading configuration: {e}")
            # Load hardcoded defaults if config file can't be read
            return {
                "display": {"rotation_interval_minutes": 60, "status_bar_height": 40},
                "photos": {"directory": "static/images/photos", "max_width": 800, "max_height": 440},
                "weather": {"update_interval_minutes": 30},
                "system": {"timezone": "UTC"}
            }
    
    def _load_fonts(self):
        """Load fonts for status bar"""
        try:
            # Try to load system fonts, fall back to default if not available
            font_path = "/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf"
            font_path_bold = "/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf"
            
            if os.path.exists(font_path):
                self.font = ImageFont.truetype(font_path, 20)
                self.font_small = ImageFont.truetype(font_path, 16)
            else:
                self.font = ImageFont.load_default()
                self.font_small = ImageFont.load_default()
                
            if os.path.exists(font_path_bold):
                self.font_bold = ImageFont.truetype(font_path_bold, 22)
            else:
                self.font_bold = ImageFont.load_default()
                
        except Exception as e:
            logger.error(f"Error loading fonts: {e}")
            self.font = ImageFont.load_default()
            self.font_small = ImageFont.load_default()
            self.font_bold = ImageFont.load_default()
    
    def _setup_signal_handlers(self):
        """Set up signal handlers for external control"""
        # SIGUSR1: Change to next photo
        signal.signal(signal.SIGUSR1, self._handle_next_photo_signal)
        
        # SIGUSR2: Change display mode
        signal.signal(signal.SIGUSR2, self._handle_mode_change_signal)
    
    def _handle_next_photo_signal(self, signum, frame):
        """Handle signal to change to next photo"""
        logger.info("Received signal to change photo")
        # We'll just set the last photo change time to trigger a change on next cycle
        self.last_photo_change = 0
    
    def _handle_mode_change_signal(self, signum, frame):
        """Handle signal to change display mode"""
        logger.info("Received signal to change display mode")
        # Cycle through display modes
        mode_list = list(DisplayMode)
        current_index = mode_list.index(self.current_mode)
        next_index = (current_index + 1) % len(mode_list)
        self.current_mode = mode_list[next_index]
        logger.info(f"Switched to display mode: {self.current_mode.name}")
    
    def load_viewed_photos(self):
        """Load the record of viewed photos with timestamps"""
        if os.path.exists(self.viewed_photos_file):
            try:
                with open(self.viewed_photos_file, 'r') as f:
                    self.viewed_photos = json.load(f)
                logger.info(f"Loaded {len(self.viewed_photos)} viewed photo records")
            except Exception as e:
                logger.error(f"Error loading viewed photos: {e}")
                self.viewed_photos = {}
        else:
            self.viewed_photos = {}
    
    def save_viewed_photos(self):
        """Save the record of viewed photos with timestamps"""
        try:
            with open(self.viewed_photos_file, 'w') as f:
                json.dump(self.viewed_photos, f)
            logger.debug("Saved viewed photos record")
        except Exception as e:
            logger.error(f"Error saving viewed photos: {e}")
    
    def get_random_photo(self):
        """Select a random photo from the library using weighted selection
        
        This method selects a photo based on several factors:
        1. How recently the photo was last shown
        2. How many times the photo has been shown
        3. Random factor to ensure variety
        
        Returns:
            str: Path to the selected photo, or None if no photos are available
        """
        photo_dir = self.config["photos"]["directory"]
        
        if not os.path.exists(photo_dir):
            logger.error(f"Photo directory not found: {photo_dir}")
            return None
        
        # Get list of photo files
        photos = []
        for filename in os.listdir(photo_dir):
            if filename.lower().endswith(('.png', '.jpg', '.jpeg', '.bmp')):
                photos.append(os.path.join(photo_dir, filename))
        
        if not photos:
            logger.warning("No photos found in photo directory")
            return None
        
        # If we've shown all photos in the current session, reset history
        if len(self.photo_history) >= len(photos):
            self.photo_history = self.photo_history[-min(5, len(photos) // 2):]
        
        # Calculate weights for each photo based on viewing history
        now = time.time()
        weights = {}
        
        for photo_path in photos:
            # Skip photos in recent history (current session)
            if photo_path in self.photo_history[-min(3, len(photos) // 4):]:  # Avoid very recent photos
                continue
                
            photo_basename = os.path.basename(photo_path)
            
            # Base weight - all photos start with the same chance
            weight = 100.0
            
            # Adjust weight based on view history
            if photo_basename in self.viewed_photos:
                record = self.viewed_photos[photo_basename]
                
                # How many times shown - reduce weight for frequently shown photos
                view_count = record.get("count", 0)
                weight -= min(50, view_count * 5)  # Reduce by 5 for each past view, max 50 reduction
                
                # How recently shown - reduce weight for recently shown photos
                last_shown = record.get("last_shown", 0)
                days_since_shown = (now - last_shown) / (24 * 3600)  # Convert to days
                
                if days_since_shown < 1:  # Shown in the last day
                    weight -= 70
                elif days_since_shown < 3:  # Shown in the last 3 days
                    weight -= 40
                elif days_since_shown < 7:  # Shown in the last week
                    weight -= 20
            
            # Add a small random factor (±15) to prevent deterministic selection
            weight += random.uniform(-15, 15)
            
            # Ensure minimum weight of 5
            weights[photo_path] = max(5, weight)
        
        # If all photos are in recent history or have zero/negative weight
        if not weights:
            # Fall back to simple selection excluding the very last photo shown
            available_photos = [p for p in photos if p != self.current_photo]
            if not available_photos:
                available_photos = photos
            selected_photo = random.choice(available_photos)
        else:
            # Weighted random selection
            photos_list = list(weights.keys())
            weights_list = list(weights.values())
            
            # Normalize weights to sum to 1.0
            total_weight = sum(weights_list)
            normalized_weights = [w/total_weight for w in weights_list]
            
            # Weighted random choice
            selected_photo = random.choices(photos_list, weights=normalized_weights, k=1)[0]
        
        # Update history
        self.photo_history.append(selected_photo)
        self.current_photo = selected_photo
        self.last_photo_change = now
        
        # Update the viewed photos record
        photo_basename = os.path.basename(selected_photo)
        if photo_basename not in self.viewed_photos:
            self.viewed_photos[photo_basename] = {"count": 0, "last_shown": 0}
            
        self.viewed_photos[photo_basename]["count"] = self.viewed_photos[photo_basename].get("count", 0) + 1
        self.viewed_photos[photo_basename]["last_shown"] = now
        
        # Save the updated record
        self.save_viewed_photos()
        
        logger.info(f"Selected photo: {selected_photo}")
        return selected_photo
    
    def create_status_bar(self, width, height):
        """Create the status bar with time and weather
        
        Args:
            width (int): Width of the status bar
            height (int): Height of the status bar
            
        Returns:
            PIL.Image: Status bar image
        """
        # Configure image mode based on display mode
        image_mode = 'L' if self.display.grayscale_mode else '1'
        bg_color = 255  # White background
        fg_color = 0    # Black text/lines
        
        # Create a blank status bar
        status_bar = Image.new(image_mode, (width, height), bg_color)
        draw = ImageDraw.Draw(status_bar)
        
        # Draw a top border
        draw.line([(0, 0), (width, 0)], fill=fg_color, width=1)
        
        # Get current time with timezone support
        timezone_name = self.config["system"].get("timezone", "UTC")
        try:
            tz = pytz.timezone(timezone_name)
            now = datetime.now(tz)
        except:
            logger.warning(f"Invalid timezone: {timezone_name}, using system time")
            now = datetime.now()
            
        # Format time based on locale settings
        time_format = self.config["display"].get("time_format", "%I:%M %p")
        date_format = self.config["display"].get("date_format", "%b %d, %Y")
        
        try:
            time_str = now.strftime(time_format)
            date_str = now.strftime(date_format)
            datetime_str = f"{time_str} - {date_str}"
        except:
            # Fall back to default format if custom format fails
            datetime_str = now.strftime("%I:%M %p - %b %d, %Y")
        
        # Draw the time on the left
        draw.text((10, 9), datetime_str, font=self.font, fill=fg_color)
        
        # Update weather if needed
        current_time = time.time()
        update_interval = self.config["weather"].get("update_interval_minutes", 30) * 60
        
        if current_time - self.last_weather_update > update_interval:
            # Time to update weather
            logger.debug("Updating weather data")
            self.last_weather_update = current_time
        
        # Get weather data if available
        weather_data = self.weather_client.get_weather()
        
        if weather_data:
            # Format temperature based on units (default to Celsius)
            units = self.config["weather"].get("units", "metric")
            temp = weather_data.get("temp", "N/A")
            unit_symbol = "°C" if units == "metric" else "°F"
            
            # Get weather condition
            condition = weather_data.get("condition", "Unknown")
            
            # Get any weather alerts if available
            has_alert = weather_data.get("has_alert", False)
            
            # Draw the weather on the right
            weather_text = f"{temp}{unit_symbol} - {condition}"
            if has_alert:
                weather_text = "⚠️ " + weather_text  # Add alert indicator
                
            text_width = self.font.getbbox(weather_text)[2]
            draw.text((width - text_width - 10, 9), weather_text, font=self.font, fill=fg_color)
        else:
            # Draw placeholder if no weather
            draw.text((width - 150, 10), "Weather unavailable", font=self.font_small, fill=fg_color)
        
        return status_bar
    
    def create_clock_display(self):
        """Create a large clock display with date and weather
        
        Returns:
            PIL.Image: Clock display image
        """
        display_width = self.display.width
        display_height = self.display.height
        
        # Configure image mode based on display settings
        image_mode = 'L' if self.display.grayscale_mode else '1'
        bg_color = 255  # White background
        fg_color = 0    # Black text/lines
        
        # Create a blank canvas
        canvas = Image.new(image_mode, (display_width, display_height), bg_color)
        draw = ImageDraw.Draw(canvas)
        
        # Get current time with timezone support
        timezone_name = self.config["system"].get("timezone", "UTC")
        try:
            tz = pytz.timezone(timezone_name)
            now = datetime.now(tz)
        except:
            logger.warning(f"Invalid timezone: {timezone_name}, using system time")
            now = datetime.now()
        
        # Draw large time in center
        time_str = now.strftime("%I:%M")
        am_pm = now.strftime("%p")
        
        # Use a really large font for the time (or default if not available)
        large_font = None
        font_path = "/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf"
        
        if os.path.exists(font_path):
            try:
                large_font = ImageFont.truetype(font_path, 160)
            except:
                large_font = None
        
        if large_font is None:
            large_font = self.font_bold
        
        # Get text size and position it centrally
        time_bbox = large_font.getbbox(time_str)
        time_width = time_bbox[2] - time_bbox[0]
        time_height = time_bbox[3] - time_bbox[1]
        
        time_x = (display_width - time_width) // 2
        time_y = (display_height - time_height) // 2 - 60  # Shift up to make room for date
        
        # Draw the time
        draw.text((time_x, time_y), time_str, font=large_font, fill=fg_color)
        
        # Draw AM/PM to the right of the time
        am_pm_bbox = self.font_bold.getbbox(am_pm)
        am_pm_width = am_pm_bbox[2] - am_pm_bbox[0]
        am_pm_x = time_x + time_width + 10
        am_pm_y = time_y + 20  # Align near the top of the time
        draw.text((am_pm_x, am_pm_y), am_pm, font=self.font_bold, fill=fg_color)
        
        # Draw date below the time
        date_str = now.strftime("%A, %B %d, %Y")
        date_bbox = self.font_bold.getbbox(date_str)
        date_width = date_bbox[2] - date_bbox[0]
        date_x = (display_width - date_width) // 2
        date_y = time_y + time_height + 20
        
        draw.text((date_x, date_y), date_str, font=self.font_bold, fill=fg_color)
        
        # Get weather data if available and draw at bottom
        weather_data = self.weather_client.get_weather()
        
        if weather_data:
            # Format temperature based on units (default to Celsius)
            units = self.config["weather"].get("units", "metric")
            temp = weather_data.get("temp", "N/A")
            unit_symbol = "°C" if units == "metric" else "°F"
            
            # Get weather condition and icon if available
            condition = weather_data.get("condition", "Unknown")
            
            # Format weather text
            weather_text = f"{temp}{unit_symbol} - {condition}"
            
            weather_bbox = self.font_bold.getbbox(weather_text)
            weather_width = weather_bbox[2] - weather_bbox[0]
            weather_x = (display_width - weather_width) // 2
            weather_y = date_y + 60
            
            draw.text((weather_x, weather_y), weather_text, font=self.font_bold, fill=fg_color)
            
            # If we have forecast data, show it
            forecast = weather_data.get("forecast", [])
            if forecast and len(forecast) > 0:
                forecast_y = weather_y + 40
                forecast_text = "Forecast: " + ", ".join([f"{item.get('day', '')}: {item.get('temp', '')}°" for item in forecast[:3]])
                
                forecast_bbox = self.font.getbbox(forecast_text)
                forecast_width = forecast_bbox[2] - forecast_bbox[0]
                forecast_x = (display_width - forecast_width) // 2
                
                draw.text((forecast_x, forecast_y), forecast_text, font=self.font, fill=fg_color)
        
        return canvas
    
    def create_info_display(self):
        """Create a system information display
        
        Returns:
            PIL.Image: Information display image
        """
        display_width = self.display.width
        display_height = self.display.height
        
        # Configure image mode based on display settings
        image_mode = 'L' if self.display.grayscale_mode else '1'
        bg_color = 255  # White background
        fg_color = 0    # Black text/lines
        
        # Create a blank canvas
        canvas = Image.new(image_mode, (display_width, display_height), bg_color)
        draw = ImageDraw.Draw(canvas)
        
        # Draw title
        title = "InkFrame Status Information"
        title_bbox = self.font_bold.getbbox(title)
        title_width = title_bbox[2] - title_bbox[0]
        title_x = (display_width - title_width) // 2
        
        draw.text((title_x, 30), title, font=self.font_bold, fill=fg_color)
        draw.line([(50, 70), (display_width - 50, 70)], fill=fg_color, width=1)
        
        # Get system information
        # Time running
        now = time.time()
        uptime_seconds = now - self.last_photo_change
        minutes, seconds = divmod(uptime_seconds, 60)
        hours, minutes = divmod(minutes, 60)
        days, hours = divmod(hours, 24)
        
        if days > 0:
            uptime_str = f"{int(days)}d {int(hours)}h {int(minutes)}m"
        elif hours > 0:
            uptime_str = f"{int(hours)}h {int(minutes)}m {int(seconds)}s"
        else:
            uptime_str = f"{int(minutes)}m {int(seconds)}s"
        
        # Photo statistics
        total_photos = len([f for f in os.listdir(self.config["photos"]["directory"]) 
                          if f.lower().endswith(('.png', '.jpg', '.jpeg', '.bmp'))])
        viewed_photos = len(self.viewed_photos)
        
        # Current settings
        interval = self.config["display"].get("rotation_interval_minutes", 60)
        display_mode = "Grayscale" if self.display.grayscale_mode else "Black & White"
        dithering = "Enabled" if self.config["display"].get("enable_dithering", True) else "Disabled"
        
        # Format information lines
        info_lines = [
            f"Current Time: {datetime.now().strftime('%I:%M:%S %p - %b %d, %Y')}",
            f"Time Since Last Change: {uptime_str}",
            f"Photos Available: {total_photos}",
            f"Photos Viewed: {viewed_photos}",
            f"Rotation Interval: {interval} minutes",
            f"Display Mode: {display_mode}",
            f"Dithering: {dithering}",
            f"Current Mode: {self.current_mode.name}"
        ]
        
        # Draw each line of information
        y_position = 100
        for line in info_lines:
            draw.text((50, y_position), line, font=self.font, fill=fg_color)
            y_position += 40
        
        # Add weather data if available
        weather_data = self.weather_client.get_weather()
        if weather_data:
            draw.line([(50, y_position), (display_width - 50, y_position)], fill=fg_color, width=1)
            y_position += 30
            
            weather_title = "Weather Information"
            draw.text(((display_width - self.font_bold.getbbox(weather_title)[2]) // 2, y_position), 
                     weather_title, font=self.font_bold, fill=fg_color)
            y_position += 40
            
            # Basic weather info
            units = self.config["weather"].get("units", "metric")
            temp = weather_data.get("temp", "N/A")
            unit_symbol = "°C" if units == "metric" else "°F"
            condition = weather_data.get("condition", "Unknown")
            
            weather_lines = [
                f"Current: {temp}{unit_symbol} - {condition}",
                f"Humidity: {weather_data.get('humidity', 'N/A')}%",
                f"Wind: {weather_data.get('wind_speed', 'N/A')} {weather_data.get('wind_direction', '')}"
            ]
            
            for line in weather_lines:
                draw.text((50, y_position), line, font=self.font, fill=fg_color)
                y_position += 40
        
        return canvas
    
    def display_photo(self, photo_path=None, force_refresh=False):
        """Display a photo with status bar
        
        Args:
            photo_path (str, optional): Path to photo to display. If None, a random photo is selected.
            force_refresh (bool): Whether to force a full display refresh
            
        Returns:
            bool: True if successful, False otherwise
        """
        if not photo_path:
            photo_path = self.get_random_photo()
            
        if not photo_path or not os.path.exists(photo_path):
            logger.error(f"Invalid photo path: {photo_path}")
            # Display error message on e-ink display
            return self._display_error_message("Photo not found")
        
        try:
            # Open and prepare the photo
            photo = Image.open(photo_path)
            
            # Calculate dimensions
            display_width = self.display.width
            display_height = self.display.height
            status_bar_height = self.config["display"]["status_bar_height"]
            photo_height = display_height - status_bar_height
            
            # Configure image mode based on display settings
            image_mode = 'L' if self.display.grayscale_mode else '1'
            bg_color = 255  # White background
            
            # Resize photo while maintaining aspect ratio
            photo_ratio = photo.width / photo.height
            display_ratio = display_width / photo_height
            
            if photo_ratio > display_ratio:
                # Photo is wider than display ratio
                new_width = display_width
                new_height = int(display_width / photo_ratio)
            else:
                # Photo is taller than display ratio
                new_height = photo_height
                new_width = int(photo_height * photo_ratio)
            
            # Use high-quality resizing
            photo = photo.resize((new_width, new_height), Image.Resampling.LANCZOS)
            
            # Create a white canvas for the display
            canvas = Image.new(image_mode, (display_width, display_height), bg_color)
            
            # Calculate position to center the photo
            x_offset = (display_width - new_width) // 2
            y_offset = (photo_height - new_height) // 2
            
            # Convert photo to appropriate mode
            if image_mode == 'L' and photo.mode != 'L':
                photo = photo.convert('L')
            elif image_mode == '1' and photo.mode != '1':
                photo = photo.convert('1')
            
            # Paste the photo onto the canvas
            canvas.paste(photo, (x_offset, y_offset))
            
            # Create and add the status bar at the bottom
            status_bar = self.create_status_bar(display_width, status_bar_height)
            canvas.paste(status_bar, (0, photo_height))
            
            # Display the composite image
            self.display.display_image_buffer(canvas, force_refresh)
            
            logger.info(f"Displayed photo with status bar: {photo_path}")
            return True
            
        except Exception as e:
            logger.error(f"Error displaying photo: {e}")
            return self._display_error_message(f"Error: {str(e)[:50]}...")
    
    def _display_error_message(self, message):
        """Display an error message on the e-ink screen
        
        Args:
            message (str): Error message to display
            
        Returns:
            bool: True if successful, False otherwise
        """
        try:
            display_width = self.display.width
            display_height = self.display.height
            
            # Configure image mode based on display settings
            image_mode = 'L' if self.display.grayscale_mode else '1'
            bg_color = 255  # White background
            fg_color = 0    # Black text
            
            # Create a white canvas
            canvas = Image.new(image_mode, (display_width, display_height), bg_color)
            draw = ImageDraw.Draw(canvas)
            
            # Draw error box
            margin = 60
            draw.rectangle([
                (margin, margin),
                (display_width - margin, display_height - margin)
            ], outline=fg_color, width=2)
            
            # Draw error title
            title = "InkFrame Error"
            title_bbox = self.font_bold.getbbox(title)
            title_width = title_bbox[2] - title_bbox[0]
            title_x = (display_width - title_width) // 2
            draw.text((title_x, margin + 30), title, font=self.font_bold, fill=fg_color)
            
            # Draw error message
            msg_bbox = self.font.getbbox(message)
            msg_width = msg_bbox[2] - msg_bbox[0]
            msg_x = (display_width - msg_width) // 2
            draw.text((msg_x, display_height // 2), message, font=self.font, fill=fg_color)
            
            # Draw timestamp
            timestamp = f"Time: {datetime.now().strftime('%I:%M:%S %p - %b %d, %Y')}"
            ts_bbox = self.font_small.getbbox(timestamp)
            ts_width = ts_bbox[2] - ts_bbox[0]
            ts_x = (display_width - ts_width) // 2
            draw.text((ts_x, display_height - margin - 40), timestamp, font=self.font_small, fill=fg_color)
            
            # Display the error canvas
            self.display.display_image_buffer(canvas, True)  # Force full refresh for errors
            
            logger.info(f"Displayed error message: {message}")
            return True
            
        except Exception as e:
            logger.error(f"Error displaying error message: {e}")
            return False
    
    def display_current_mode(self, force_refresh=False):
        """Display content based on current display mode
        
        Args:
            force_refresh (bool): Whether to force a full display refresh
            
        Returns:
            bool: True if successful, False otherwise
        """
        if self.current_mode == DisplayMode.PHOTO:
            return self.display_photo(force_refresh=force_refresh)
            
        elif self.current_mode == DisplayMode.CLOCK:
            clock_display = self.create_clock_display()
            return self.display.display_image_buffer(clock_display, force_refresh)
            
        elif self.current_mode == DisplayMode.INFO:
            info_display = self.create_info_display()
            return self.display.display_image_buffer(info_display, force_refresh)
            
        elif self.current_mode == DisplayMode.WEATHER:
            # TODO: Implement detailed weather display
            # For now, fall back to photo mode
            self.current_mode = DisplayMode.PHOTO
            return self.display_photo(force_refresh=force_refresh)
            
        else:
            logger.error(f"Unknown display mode: {self.current_mode}")
            self.current_mode = DisplayMode.PHOTO
            return self.display_photo(force_refresh=force_refresh)
    
    def run_photo_cycle(self):
        """Run the main photo display cycle"""
        logger.info("Starting photo display cycle")
        
        try:
            # Do an initial display
            force_refresh = True  # Force refresh on first display
            self.display_current_mode(force_refresh)
            
            while True:
                # Check if it's time to change the photo
                now = time.time()
                interval_minutes = self.config["display"]["rotation_interval_minutes"]
                interval_seconds = interval_minutes * 60
                
                force_refresh = False  # Default to partial refresh for regular updates
                
                # Every 12 hours or every 10 rotations, do a full refresh to reduce ghosting
                twelve_hours = 12 * 60 * 60
                if (now - self.last_photo_change >= twelve_hours) or (now % (10 * interval_seconds) < interval_seconds):
                    force_refresh = True
                    logger.info("Performing periodic full refresh to reduce ghosting")
                
                # Check if it's time for a photo change
                if now - self.last_photo_change >= interval_seconds:
                    logger.info(f"Rotation interval reached, updating display")
                    self.display_current_mode(force_refresh)
                
                # Sleep for a while (check more frequently than the full interval)
                # This allows us to respond to signals and changes more promptly
                check_interval = min(60, interval_seconds // 4)  # Check at least every minute, or more often for short intervals
                time.sleep(check_interval)
                
        except KeyboardInterrupt:
            logger.info("Photo cycle interrupted by user")
        except Exception as e:
            logger.error(f"Error in photo cycle: {e}")
            # Try to display the error
            try:
                self._display_error_message(f"Cycle error: {str(e)[:50]}...")
            except:
                pass
        finally:
            # Clean up resources
            self.display.sleep()
            self.display.close()
            logger.info("Photo cycle ended, display resources released")

if __name__ == "__main__":
    # Simple test when run directly
    logging.basicConfig(level=logging.INFO)
    
    import argparse
    parser = argparse.ArgumentParser(description="InkFrame Photo Manager")
    parser.add_argument("--mode", choices=["photo", "clock", "info", "weather"], 
                      help="Display mode to test")
    parser.add_argument("--photo", help="Specific photo to display")
    parser.add_argument("--test-all", action="store_true", help="Test all display modes")
    
    args = parser.parse_args()
    
    manager = PhotoManager()
    
    try:
        if args.test_all:
            # Test all display modes
            logger.info("Testing all display modes")
            
            manager.current_mode = DisplayMode.PHOTO
            logger.info("Testing PHOTO mode")
            manager.display_current_mode(True)
            time.sleep(3)
            
            manager.current_mode = DisplayMode.CLOCK
            logger.info("Testing CLOCK mode")
            manager.display_current_mode(True)
            time.sleep(3)
            
            manager.current_mode = DisplayMode.INFO
            logger.info("Testing INFO mode")
            manager.display_current_mode(True)
            time.sleep(3)
            
            logger.info("Testing error display")
            manager._display_error_message("This is a test error message")
            time.sleep(3)
            
            logger.info("All tests completed")
            
        elif args.mode:
            # Set display mode based on argument
            if args.mode == "photo":
                manager.current_mode = DisplayMode.PHOTO
            elif args.mode == "clock":
                manager.current_mode = DisplayMode.CLOCK
            elif args.mode == "info":
                manager.current_mode = DisplayMode.INFO
            elif args.mode == "weather":
                manager.current_mode = DisplayMode.WEATHER
                
            logger.info(f"Testing {args.mode.upper()} mode")
            manager.display_current_mode(True)
            
        elif args.photo:
            # Display a specific photo
            if os.path.exists(args.photo):
                logger.info(f"Displaying specific photo: {args.photo}")
                manager.display_photo(args.photo, True)
            else:
                logger.error(f"Photo not found: {args.photo}")
                manager._display_error_message(f"Photo not found: {os.path.basename(args.photo)}")
        else:
            # Default behavior - display a random photo
            logger.info("Displaying random photo")
            manager.display_photo()
        
        # Wait for a bit to see the result
        time.sleep(10)
        
    finally:
        # Clean up
        manager.display.sleep()