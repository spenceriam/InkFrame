#!/usr/bin/env python3
"""
Set timezone configuration for InkFrame
"""
import json
import os
import pytz
from datetime import datetime
import requests

def get_current_timezone_from_ip():
    """Try to detect timezone from IP location"""
    try:
        # Use a free IP geolocation service
        response = requests.get('http://ip-api.com/json/', timeout=5)
        if response.status_code == 200:
            data = response.json()
            return data.get('timezone', None)
    except:
        pass
    return None

def get_system_timezone():
    """Try to get timezone from system"""
    try:
        # Try to read from /etc/timezone (Linux)
        if os.path.exists('/etc/timezone'):
            with open('/etc/timezone', 'r') as f:
                return f.read().strip()
    except:
        pass
    
    try:
        # Try to get from environment
        tz = os.environ.get('TZ', None)
        if tz:
            return tz
    except:
        pass
    
    return None

def list_common_timezones():
    """List common US timezones"""
    common = [
        ('US/Eastern', 'Eastern Time (New York, Miami)'),
        ('US/Central', 'Central Time (Chicago, Dallas)'),
        ('US/Mountain', 'Mountain Time (Denver, Phoenix)'),
        ('US/Pacific', 'Pacific Time (Los Angeles, Seattle)'),
        ('US/Alaska', 'Alaska Time'),
        ('US/Hawaii', 'Hawaii Time'),
        ('Europe/London', 'London'),
        ('Europe/Paris', 'Paris, Berlin'),
        ('Asia/Tokyo', 'Tokyo'),
        ('Australia/Sydney', 'Sydney')
    ]
    return common

def main():
    config_path = "config/config.json"
    
    # Load current config
    if os.path.exists(config_path):
        with open(config_path, 'r') as f:
            config = json.load(f)
    else:
        # Use default config
        with open("config/default_config.json", 'r') as f:
            config = json.load(f)
    
    current_tz = config.get('system', {}).get('timezone', 'UTC')
    print(f"Current timezone: {current_tz}")
    
    # Try to detect timezone
    detected_tz = get_current_timezone_from_ip()
    if not detected_tz:
        detected_tz = get_system_timezone()
    
    if detected_tz and detected_tz != current_tz:
        print(f"\nDetected timezone: {detected_tz}")
        
        # Verify it's valid
        try:
            tz = pytz.timezone(detected_tz)
            now = datetime.now(tz)
            print(f"Current time would be: {now.strftime('%I:%M %p %Z')}")
            
            use_detected = input("\nUse detected timezone? (y/n): ").lower().strip() == 'y'
            if use_detected:
                config['system']['timezone'] = detected_tz
                with open(config_path, 'w') as f:
                    json.dump(config, f, indent=2)
                print(f"Timezone updated to: {detected_tz}")
                return
        except:
            print(f"Detected timezone '{detected_tz}' is invalid")
    
    # Show current time in various zones
    print("\nCurrent time in common timezones:")
    common = list_common_timezones()
    for i, (tz_name, desc) in enumerate(common, 1):
        tz = pytz.timezone(tz_name)
        now = datetime.now(tz)
        print(f"{i}. {desc:<30} {now.strftime('%I:%M %p')} ({tz_name})")
    
    # Let user choose
    print(f"\n0. Keep current ({current_tz})")
    print("Or enter a timezone name (e.g., 'America/New_York')")
    
    choice = input("\nSelect timezone (0-10 or timezone name): ").strip()
    
    if choice == '0':
        print("Keeping current timezone")
        return
    
    try:
        idx = int(choice)
        if 1 <= idx <= len(common):
            new_tz = common[idx-1][0]
        else:
            print("Invalid selection")
            return
    except ValueError:
        # User entered a timezone name
        new_tz = choice
    
    # Validate timezone
    try:
        tz = pytz.timezone(new_tz)
        now = datetime.now(tz)
        print(f"\nTime would be: {now.strftime('%I:%M %p %Z on %B %d, %Y')}")
        
        confirm = input("Confirm this timezone? (y/n): ").lower().strip() == 'y'
        if confirm:
            config['system']['timezone'] = new_tz
            with open(config_path, 'w') as f:
                json.dump(config, f, indent=2)
            print(f"\nTimezone updated to: {new_tz}")
            print("Restart the display service to apply changes")
        else:
            print("Timezone not changed")
    except Exception as e:
        print(f"Invalid timezone: {e}")

if __name__ == "__main__":
    main()