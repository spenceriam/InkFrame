#!/usr/bin/env python3
"""
GPIO test script with reset functionality for Waveshare e-ink display using lgpio library.
This script is designed for Raspberry Pi OS Bookworm which uses libgpio.
"""
import sys
import time
import traceback
import subprocess

print("Starting lgpio reset test for e-ink display...")

# First try to free any potentially busy GPIO pins
try:
    print("Checking for busy GPIO pins...")
    subprocess.run(["sudo", "gpioinfo"], check=False)
    
    print("Attempting to reset GPIO pins...")
    # This is a brutal approach but can help reset stuck pins
    subprocess.run(["sudo", "systemctl", "restart", "pigpiod"], check=False)
    subprocess.run(["sudo", "killall", "pigpiod"], check=False)
    time.sleep(2)  # Give system time to release resources
    
    # Also try GPIO group permission fix
    print("Fixing GPIO permissions...")
    subprocess.run(["sudo", "usermod", "-aG", "gpio", "$(whoami)"], check=False, shell=True)
    
except Exception as reset_error:
    print(f"Reset error: {reset_error}")

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
    
    # Set up GPIO with better error handling
    print("Opening GPIO chip...")
    h = lgpio.gpiochip_open(0)  # Use chip 0 for Pi Zero, 4 for Pi 5
    
    print("Setting up GPIO pins one by one with error handling...")
    
    # Try each pin separately with error handling
    pins_claimed = []
    
    try:
        print(f"Claiming RST_PIN ({RST_PIN})...")
        lgpio.gpio_claim_output(h, RST_PIN)
        pins_claimed.append(RST_PIN)
        print(f"  Success: RST_PIN ({RST_PIN}) claimed")
    except Exception as e:
        print(f"  Error claiming RST_PIN ({RST_PIN}): {e}")
    
    try:
        print(f"Claiming DC_PIN ({DC_PIN})...")
        lgpio.gpio_claim_output(h, DC_PIN)
        pins_claimed.append(DC_PIN)
        print(f"  Success: DC_PIN ({DC_PIN}) claimed")
    except Exception as e:
        print(f"  Error claiming DC_PIN ({DC_PIN}): {e}")
    
    try:
        print(f"Claiming CS_PIN ({CS_PIN})...")
        lgpio.gpio_claim_output(h, CS_PIN)
        pins_claimed.append(CS_PIN)
        print(f"  Success: CS_PIN ({CS_PIN}) claimed")
    except Exception as e:
        print(f"  Error claiming CS_PIN ({CS_PIN}): {e}")
    
    try:
        print(f"Claiming BUSY_PIN ({BUSY_PIN})...")
        lgpio.gpio_claim_input(h, BUSY_PIN)
        pins_claimed.append(BUSY_PIN)
        print(f"  Success: BUSY_PIN ({BUSY_PIN}) claimed")
    except Exception as e:
        print(f"  Error claiming BUSY_PIN ({BUSY_PIN}): {e}")
    
    # Test GPIO toggling for pins we successfully claimed
    print("\nTesting GPIO pins that were successfully claimed...")
    for pin in pins_claimed:
        if pin != BUSY_PIN:  # Only toggle output pins
            try:
                lgpio.gpio_write(h, pin, 1)
                time.sleep(0.5)
                lgpio.gpio_write(h, pin, 0)
                time.sleep(0.5)
                lgpio.gpio_write(h, pin, 1)
                print(f"Pin {pin} toggled successfully")
            except Exception as toggle_error:
                print(f"Error toggling pin {pin}: {toggle_error}")
    
    # Check BUSY pin if we claimed it
    if BUSY_PIN in pins_claimed:
        try:
            busy_status = lgpio.gpio_read(h, BUSY_PIN)
            print(f"BUSY pin (pin {BUSY_PIN}) status: {'HIGH' if busy_status else 'LOW'}")
        except Exception as busy_error:
            print(f"Error reading BUSY pin: {busy_error}")
    
    # Test SPI separately with better error handling
    print("\nTesting SPI interface...")
    spi_success = False
    try:
        spi_handle = lgpio.spi_open(0, 0, 4000000, 0)  # Bus 0, CE0, 4MHz, mode 0
        print("SPI connection established")
        
        # Try sending data over SPI
        print("Sending test data over SPI...")
        resp = lgpio.spi_xfer(spi_handle, [0x70, 0x01])  # Send arbitrary data
        print(f"SPI response: {resp}")
        
        # Close SPI
        lgpio.spi_close(spi_handle)
        print("SPI closed successfully")
        spi_success = True
        
    except Exception as spi_error:
        print(f"SPI error: {spi_error}")
    
    # Clean up GPIO
    print("\nCleaning up GPIO...")
    lgpio.gpiochip_close(h)
    
    print("\nDIAGNOSTICS:")
    print(f"GPIO pins claimed: {pins_claimed}")
    print(f"SPI test: {'SUCCESS' if spi_success else 'FAILED'}")
    
    print("\nTROUBLESHOOTING TIPS:")
    print("1. If pins are busy, try rebooting the Raspberry Pi")
    print("2. Some pins may be in use by other processes - check with 'sudo gpioinfo'")
    print("3. For SPI issues, check if SPI is enabled with 'sudo raspi-config'")
    print("4. Try changing pin assignments if specific pins are problematic")
    print("5. For persistent issues, check hardware connections and power supply")

except ImportError as e:
    print(f"ERROR: Failed to import a required library: {e}")
    print("Make sure lgpio is installed with: sudo apt install python3-lgpio")
    
except Exception as e:
    print(f"ERROR: Unexpected error: {e}")
    print(traceback.format_exc())