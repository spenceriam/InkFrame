#!/usr/bin/env python3
"""
Configuration manager for InkFrame.
Handles loading, saving, and validating configuration.
"""
import os
import sys
import logging
import json
import shutil

logger = logging.getLogger(__name__)

class ConfigManager:
    """Manages configuration for InkFrame"""
    
    def __init__(self, config_path="config/config.json", default_config_path="config/default_config.json"):
        """Initialize the configuration manager"""
        self.config_path = config_path
        self.default_config_path = default_config_path
        self.config = self.load_config()
    
    def load_config(self):
        """Load configuration from file, or create from default if it doesn't exist"""
        try:
            # If config doesn't exist, create it from default
            if not os.path.exists(self.config_path):
                logger.info(f"Config file not found, creating from default: {self.config_path}")
                self._create_default_config()
            
            # Load the config
            with open(self.config_path, 'r') as f:
                config = json.load(f)
            
            logger.info(f"Loaded configuration from {self.config_path}")
            return config
            
        except Exception as e:
            logger.error(f"Error loading configuration: {e}")
            logger.info("Loading default configuration")
            return self._load_default_config()
    
    def _create_default_config(self):
        """Create a new config file from the default config"""
        try:
            # Ensure directory exists
            os.makedirs(os.path.dirname(self.config_path), exist_ok=True)
            
            # Copy default config to config path
            if os.path.exists(self.default_config_path):
                shutil.copy(self.default_config_path, self.config_path)
                logger.info(f"Created config file from default: {self.config_path}")
            else:
                # If default config doesn't exist, create a minimal config
                self._create_minimal_config()
                
        except Exception as e:
            logger.error(f"Error creating default configuration: {e}")
            self._create_minimal_config()
    
    def _create_minimal_config(self):
        """Create a minimal configuration file if default is unavailable"""
        minimal_config = {
            "display": {
                "rotation_interval_minutes": 60,
                "status_bar_height": 40,
                "enable_dithering": True
            },
            "photos": {
                "directory": "static/images/photos",
                "max_width": 800,
                "max_height": 440,
                "format": "bmp"
            },
            "weather": {
                "api_key": "",
                "city": "",
                "country": "",
                "units": "metric",
                "update_interval_minutes": 30,
                "cache_expiry_minutes": 120
            },
            "system": {
                "timezone": "UTC",
                "web_port": 5000,
                "debug_mode": False,
                "log_level": "INFO"
            }
        }
        
        try:
            # Ensure directory exists
            os.makedirs(os.path.dirname(self.config_path), exist_ok=True)
            
            # Write minimal config
            with open(self.config_path, 'w') as f:
                json.dump(minimal_config, f, indent=2)
                
            logger.info(f"Created minimal config file: {self.config_path}")
            
        except Exception as e:
            logger.error(f"Error creating minimal configuration: {e}")
    
    def _load_default_config(self):
        """Load the default configuration"""
        try:
            if os.path.exists(self.default_config_path):
                with open(self.default_config_path, 'r') as f:
                    config = json.load(f)
                logger.info(f"Loaded default configuration from {self.default_config_path}")
                return config
            else:
                logger.error(f"Default config file not found: {self.default_config_path}")
                # Return hardcoded minimal config
                return {
                    "display": {"rotation_interval_minutes": 60, "status_bar_height": 40},
                    "photos": {"directory": "static/images/photos", "max_width": 800, "max_height": 440},
                    "weather": {"update_interval_minutes": 30},
                    "system": {"timezone": "UTC", "web_port": 5000}
                }
        except Exception as e:
            logger.error(f"Error loading default configuration: {e}")
            # Return hardcoded minimal config
            return {
                "display": {"rotation_interval_minutes": 60, "status_bar_height": 40},
                "photos": {"directory": "static/images/photos", "max_width": 800, "max_height": 440},
                "weather": {"update_interval_minutes": 30},
                "system": {"timezone": "UTC", "web_port": 5000}
            }
    
    def save_config(self, config=None):
        """Save the configuration to file"""
        if config:
            self.config = config
            
        try:
            # Ensure directory exists
            os.makedirs(os.path.dirname(self.config_path), exist_ok=True)
            
            # Write config to file
            with open(self.config_path, 'w') as f:
                json.dump(self.config, f, indent=2)
                
            logger.info(f"Saved configuration to {self.config_path}")
            return True
            
        except Exception as e:
            logger.error(f"Error saving configuration: {e}")
            return False
    
    def update_config(self, updates):
        """Update the configuration with new values"""
        try:
            # Deep update the configuration
            self._deep_update(self.config, updates)
            
            # Save the updated configuration
            self.save_config()
            
            logger.info("Configuration updated")
            return True
            
        except Exception as e:
            logger.error(f"Error updating configuration: {e}")
            return False
    
    def _deep_update(self, target, source):
        """Deep update a nested dictionary"""
        for key, value in source.items():
            if key in target and isinstance(target[key], dict) and isinstance(value, dict):
                # Recursively update nested dictionaries
                self._deep_update(target[key], value)
            else:
                # Update or add the value
                target[key] = value
    
    def get(self, path, default=None):
        """Get a configuration value by path (e.g., 'display.rotation_interval_minutes')"""
        try:
            keys = path.split('.')
            value = self.config
            for key in keys:
                value = value[key]
            return value
        except (KeyError, TypeError):
            return default
    
    def set(self, path, value):
        """Set a configuration value by path"""
        try:
            keys = path.split('.')
            target = self.config
            
            # Navigate to the final containing object
            for key in keys[:-1]:
                if key not in target:
                    target[key] = {}
                target = target[key]
                
            # Set the value
            target[keys[-1]] = value
            
            # Save the updated configuration
            self.save_config()
            
            logger.info(f"Updated config: {path} = {value}")
            return True
            
        except Exception as e:
            logger.error(f"Error setting configuration: {e}")
            return False
    
    def reset_to_default(self):
        """Reset the configuration to default values"""
        try:
            if os.path.exists(self.default_config_path):
                # Load default config
                with open(self.default_config_path, 'r') as f:
                    default_config = json.load(f)
                
                # Update config with default values
                self.config = default_config
                
                # Save the updated configuration
                self.save_config()
                
                logger.info("Configuration reset to default values")
                return True
            else:
                logger.error(f"Default config file not found: {self.default_config_path}")
                return False
                
        except Exception as e:
            logger.error(f"Error resetting configuration: {e}")
            return False

if __name__ == "__main__":
    # Simple test when run directly
    logging.basicConfig(level=logging.INFO)
    
    # Initialize the config manager
    config_manager = ConfigManager()
    
    # Print the current configuration
    print(json.dumps(config_manager.config, indent=2))
    
    # Test updating a configuration value
    config_manager.set("display.rotation_interval_minutes", 30)
    
    # Print the updated configuration
    print(f"Updated rotation interval: {config_manager.get('display.rotation_interval_minutes')}")