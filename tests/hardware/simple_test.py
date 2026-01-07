#!/usr/bin/env python3
"""
Simple GPIO and SPI test script for Waveshare e-ink display.
Tests basic hardware connections without full display initialization.
"""
import sys
import time
import traceback

print("Starting simple GPIO and SPI test...")

try:
    # Test GPIO
    print("Importing RPi.GPIO...")
    import RPi.GPIO as GPIO
    
    # Check GPIO version
    print(f"RPi.GPIO version: {GPIO.VERSION}")
    
    # Print RPi board info
    print(f"Board revision: {GPIO.RPI_INFO['P1_REVISION']}")
    print(f"Board type: {GPIO.RPI_INFO['TYPE']}")
    
    # Set up GPIO pins for e-ink display
    # These are typical pins used for Waveshare e-ink display
    RST_PIN = 17
    DC_PIN = 25
    CS_PIN = 8
    BUSY_PIN = 24
    
    # Set up GPIO
    print("Setting up GPIO pins...")
    GPIO.setmode(GPIO.BCM)
    GPIO.setup(RST_PIN, GPIO.OUT)
    GPIO.setup(DC_PIN, GPIO.OUT)
    GPIO.setup(CS_PIN, GPIO.OUT)
    GPIO.setup(BUSY_PIN, GPIO.IN)
    
    # Test basic GPIO toggling
    print("Testing GPIO pins (RST, DC, CS)...")
    for pin in [RST_PIN, DC_PIN, CS_PIN]:
        GPIO.output(pin, GPIO.HIGH)
        time.sleep(0.5)
        GPIO.output(pin, GPIO.LOW)
        time.sleep(0.5)
        GPIO.output(pin, GPIO.HIGH)
        print(f"Pin {pin} toggled")
    
    # Check status of BUSY pin
    busy_status = GPIO.input(BUSY_PIN)
    print(f"BUSY pin (pin {BUSY_PIN}) status: {'HIGH' if busy_status else 'LOW'}")
    
    # Test SPI
    print("Testing SPI interface...")
    try:
        import spidev
        print("SPI module imported successfully")
        
        spi = spidev.SpiDev()
        print("Opening SPI device 0.0...")
        spi.open(0, 0)  # Open SPI bus 0, device 0
        spi.max_speed_hz = 4000000  # Set SPI speed to 4MHz
        spi.mode = 0
        print("SPI connection established")
        
        # Try sending data over SPI
        print("Sending test data over SPI...")
        resp = spi.xfer2([0x70, 0x01])  # Send arbitrary data
        print(f"SPI response: {resp}")
        
        # Close SPI
        spi.close()
        print("SPI closed")
        
    except ImportError:
        print("ERROR: Could not import spidev module")
        print("Make sure SPI is enabled in raspi-config")
    except Exception as spi_error:
        print(f"SPI error: {spi_error}")
        print(f"SPI trace: {traceback.format_exc()}")
    
    # Test for Waveshare library
    print("\nChecking for Waveshare e-paper library...")
    try:
        # Try to import the Waveshare library
        import importlib
        waveshare_modules = [
            'epd7in5',      # Regular 7.5 inch
            'epd7in5_V2',   # 7.5 inch V2
            'epd7in5_HD',   # 7.5 inch HD
            'epd7in5b_V2'   # 7.5 inch B&W/Red V2
        ]
        
        found_modules = []
        for module_name in waveshare_modules:
            try:
                # Try to find the module without importing
                module_spec = importlib.util.find_spec(f"waveshare_epd.{module_name}")
                if module_spec is not None:
                    found_modules.append(module_name)
            except:
                pass
        
        if found_modules:
            print(f"Found Waveshare modules: {', '.join(found_modules)}")
        else:
            print("No Waveshare modules found")
            
    except Exception as lib_error:
        print(f"Error checking libraries: {lib_error}")
    
    # Clean up GPIO
    print("\nCleaning up GPIO...")
    GPIO.cleanup()
    
    print("\nTEST SUMMARY:")
    print("✓ GPIO test completed")
    print("✓ SPI test completed")
    print(f"✓ GPIO BUSY status: {'HIGH' if busy_status else 'LOW'}")
    print(f"✓ Found modules: {', '.join(found_modules) if 'found_modules' in locals() and found_modules else 'None'}")
    print("\nIf all tests passed, hardware connections should be good.")
    print("If SPI or GPIO tests failed, check your hardware connections and raspi-config settings.")

except ImportError as e:
    print(f"ERROR: Failed to import a required library: {e}")
    print("Make sure RPi.GPIO is installed with: pip install RPi.GPIO")
    
except Exception as e:
    print(f"ERROR: Unexpected error: {e}")
    print(traceback.format_exc())