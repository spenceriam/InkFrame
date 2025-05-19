#!/usr/bin/env python3
"""
Basic e-ink display test
A minimal test to initialize and clear an e-ink display
"""
import time
import sys
import traceback

print("Starting basic e-ink display test...")

try:
    # Import the display driver
    print("Importing 7.5 inch V2 display driver...")
    from waveshare_epd import epd7in5_V2
    print("Successfully imported display driver")
    
    # Create the display object
    print("Creating display object...")
    epd = epd7in5_V2.EPD()
    print(f"Display dimensions: {epd.width} x {epd.height}")
    
    # Print configuration information
    print("\nDisplay configuration:")
    print(f"RST_PIN: {epd7in5_V2.epdconfig.RST_PIN}")
    print(f"DC_PIN: {epd7in5_V2.epdconfig.DC_PIN}")
    print(f"BUSY_PIN: {epd7in5_V2.epdconfig.BUSY_PIN}")
    print(f"CS_PIN: {epd7in5_V2.epdconfig.CS_PIN}")
    
    # Initialize the display with extra error handling
    print("\nInitializing display...")
    print("This may take 10-15 seconds - please wait...")
    
    # Initialize with explicit timeout tracking
    init_start_time = time.time()
    init_timeout = 20  # seconds
    
    try:
        epd.init()
        init_duration = time.time() - init_start_time
        print(f"Display initialized successfully! (took {init_duration:.1f} seconds)")
    except Exception as init_error:
        print(f"Display initialization failed after {time.time() - init_start_time:.1f} seconds")
        print(f"Error: {init_error}")
        print("Trying to continue anyway...")
    
    # Try to clear the display
    print("\nClearing display...")
    clear_start_time = time.time()
    
    try:
        epd.Clear()
        clear_duration = time.time() - clear_start_time
        print(f"Display cleared successfully! (took {clear_duration:.1f} seconds)")
    except Exception as clear_error:
        print(f"Failed to clear display: {clear_error}")
    
    # Sleep the display
    print("\nPutting display to sleep...")
    try:
        epd.sleep()
        print("Display is now in sleep mode")
    except Exception as sleep_error:
        print(f"Failed to put display to sleep: {sleep_error}")
    
    print("\nTest completed!")

except ImportError:
    print("ERROR: Could not import the Waveshare display driver")
    print("Make sure the waveshare_epd directory exists and contains the driver files")
    
    # Additional helpful information
    import os
    if os.path.exists("waveshare_epd"):
        print("\nThe waveshare_epd directory exists, checking for driver files...")
        driver_files = os.listdir("waveshare_epd")
        print(f"Found {len(driver_files)} files in waveshare_epd/")
        if driver_files:
            print("First few files:", driver_files[:5])
        
        if "epd7in5_V2.py" not in driver_files:
            print("WARNING: epd7in5_V2.py is missing!")
            print("Try running: cp -r waveshare_repo/RaspberryPi_JetsonNano/python/lib/waveshare_epd/*.py waveshare_epd/")
    else:
        print("\nThe waveshare_epd directory does not exist!")
        print("Try running these commands:")
        print("git clone https://github.com/waveshare/e-Paper.git waveshare_repo")
        print("mkdir -p waveshare_epd")
        print("cp -r waveshare_repo/RaspberryPi_JetsonNano/python/lib/waveshare_epd/*.py waveshare_epd/")
        
except Exception as e:
    print(f"Unexpected error: {e}")
    print("\nDetailed error information:")
    traceback.print_exc()
    
finally:
    print("\nTest execution completed")
    print("If you didn't see any output on your e-ink display, please check:")
    print("1. Hardware connections between Raspberry Pi and e-ink HAT")
    print("2. Power supply (use a good quality 5V/2.5A+ power supply)")
    print("3. SPI interface is enabled (sudo raspi-config)")
    print("4. Try disconnecting power and reconnecting everything")