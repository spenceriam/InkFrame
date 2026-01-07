#!/usr/bin/env python3
"""
Simple GPIO pin existence check script for Raspberry Pi OS Bookworm.
This script tries different GPIO related packages to help determine which 
interface should be used for the e-ink display driver.
"""
import sys
import traceback

print("Checking available GPIO interfaces...")

# Dictionary to track available interfaces
interfaces = {
    "RPi.GPIO": False,
    "lgpio": False,
    "gpiod": False,
    "pigpio": False,
    "rpi_lgpio": False,
    "spidev": False
}

# Check RPi.GPIO
try:
    import RPi.GPIO
    interfaces["RPi.GPIO"] = True
    print("✓ RPi.GPIO is available, version:", RPi.GPIO.VERSION)
except ImportError:
    print("✗ RPi.GPIO is not available")
except Exception as e:
    print(f"✗ RPi.GPIO error: {e}")

# Check lgpio
try:
    import lgpio
    interfaces["lgpio"] = True
    print("✓ lgpio is available")
except ImportError:
    print("✗ lgpio is not available")
except Exception as e:
    print(f"✗ lgpio error: {e}")

# Check gpiod
try:
    import gpiod
    interfaces["gpiod"] = True
    print("✓ gpiod is available")
except ImportError:
    print("✗ gpiod is not available")
except Exception as e:
    print(f"✗ gpiod error: {e}")

# Check pigpio
try:
    import pigpio
    interfaces["pigpio"] = True
    print("✓ pigpio is available")
except ImportError:
    print("✗ pigpio is not available")
except Exception as e:
    print(f"✗ pigpio error: {e}")

# Check rpi_lgpio (compatibility layer)
try:
    import rpi_lgpio
    interfaces["rpi_lgpio"] = True
    print("✓ rpi_lgpio (compatibility layer) is available")
except ImportError:
    print("✗ rpi_lgpio (compatibility layer) is not available")
except Exception as e:
    print(f"✗ rpi_lgpio error: {e}")

# Check spidev
try:
    import spidev
    interfaces["spidev"] = True
    print("✓ spidev is available")
except ImportError:
    print("✗ spidev is not available")
except Exception as e:
    print(f"✗ spidev error: {e}")

# Summarize findings
print("\nSUMMARY:")
for interface, available in interfaces.items():
    print(f"{interface}: {'Available' if available else 'Not available'}")

# Make recommendations
print("\nRECOMMENDATIONS:")
if interfaces["RPi.GPIO"]:
    print("- You can use the original test scripts (simple_test.py, basic_test.py)")
elif interfaces["lgpio"]:
    print("- Use lgpio_test.py or lgpio_reset_test.py")
    print("- Install missing packages: sudo apt install python3-lgpio")
elif interfaces["gpiod"]:
    print("- Use a gpiod-based approach")
    print("- Install missing packages: sudo apt install python3-gpiod")
else:
    print("- No suitable GPIO interface found!")
    print("- Try installing one of these packages:")
    print("  sudo apt install python3-lgpio")
    print("  sudo apt install python3-gpiod")
    print("  sudo apt install python3-pigpio")
    print("  pip3 install rpi-lgpio")

if not interfaces["spidev"]:
    print("- SPI interface is missing, install with: sudo apt install python3-spidev")
    print("- Make sure SPI is enabled: sudo raspi-config → Interface Options → SPI → Enable")