#!/usr/bin/env python3
"""
GPIO test script for Waveshare e-ink display using lgpio library.
This script is designed for Raspberry Pi OS Bookworm which uses libgpio.
"""
import sys
import time
import traceback

print("Starting lgpio test for e-ink display...")

try:
    # Test lgpio
    print("Importing lgpio...")
    import lgpio
    
    # Define pins for e-ink display
    # These are typical pins used for Waveshare e-ink display
    RST_PIN = 17
    DC_PIN = 25
    CS_PIN = 8
    BUSY_PIN = 24
    
    # Set up GPIO
    print("Opening GPIO chip...")
    h = lgpio.gpiochip_open(0)  # Use chip 0 for Pi Zero, 4 for Pi 5
    
    print("Setting up GPIO pins...")
    lgpio.gpio_claim_output(h, RST_PIN)
    lgpio.gpio_claim_output(h, DC_PIN)
    lgpio.gpio_claim_output(h, CS_PIN)
    lgpio.gpio_claim_input(h, BUSY_PIN)
    
    # Test basic GPIO toggling
    print("Testing GPIO pins (RST, DC, CS)...")
    for pin in [RST_PIN, DC_PIN, CS_PIN]:
        lgpio.gpio_write(h, pin, 1)
        time.sleep(0.5)
        lgpio.gpio_write(h, pin, 0)
        time.sleep(0.5)
        lgpio.gpio_write(h, pin, 1)
        print(f"Pin {pin} toggled")
    
    # Check status of BUSY pin
    busy_status = lgpio.gpio_read(h, BUSY_PIN)
    print(f"BUSY pin (pin {BUSY_PIN}) status: {'HIGH' if busy_status else 'LOW'}")
    
    # Test SPI
    print("Testing SPI interface...")
    try:
        spi_handle = lgpio.spi_open(0, 0, 4000000, 0)  # Bus 0, CE0, 4MHz, mode 0
        print("SPI connection established")
        
        # Try sending data over SPI
        print("Sending test data over SPI...")
        resp = lgpio.spi_xfer(spi_handle, [0x70, 0x01])  # Send arbitrary data
        print(f"SPI response: {resp}")
        
        # Close SPI
        lgpio.spi_close(spi_handle)
        print("SPI closed")
        
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
    lgpio.gpiochip_close(h)
    
    print("\nTEST SUMMARY:")
    print("✓ GPIO test completed")
    print("✓ SPI test completed")
    print(f"✓ GPIO BUSY status: {'HIGH' if busy_status else 'LOW'}")
    print(f"✓ Found modules: {', '.join(found_modules) if 'found_modules' in locals() and found_modules else 'None'}")
    print("\nIf all tests passed, hardware connections should be good.")
    print("If SPI or GPIO tests failed, check your hardware connections and raspi-config settings.")

except ImportError as e:
    print(f"ERROR: Failed to import a required library: {e}")
    print("Make sure lgpio is installed with: sudo apt install python3-lgpio")
    
except Exception as e:
    print(f"ERROR: Unexpected error: {e}")
    print(traceback.format_exc())