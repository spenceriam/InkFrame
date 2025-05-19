# E-Ink Display Troubleshooting Guide

This guide is designed to help troubleshoot issues with the Waveshare e-ink display used in the InkFrame project.

## Test Scripts

We've provided several test scripts to help diagnose issues:

1. **simple_test.py** - Tests GPIO and SPI communication without initializing the display
2. **basic_test.py** - A minimal test that only tries to initialize and clear the display
3. **check_model.py** - Tests different display models to find which one works with your hardware
4. **official_test.py** - An adapted version of the official Waveshare test script
5. **test_display.py** - A more detailed test that includes a visual pattern

## Common Issues and Solutions

### 1. No output on the e-ink display

**Possible causes:**

- **Hardware connection issues**
  - Ensure the HAT is properly seated on the GPIO pins
  - Check for bent pins
  - Try reseating the HAT after disconnecting power

- **Power issues**
  - Use a good quality power supply (5V/2.5A or better)
  - Some displays need more power during initialization

- **SPI not enabled**
  - Enable SPI interface: `sudo raspi-config` → Interface Options → SPI → Enable
  - Check if SPI is loaded: `lsmod | grep spi` (should show spi_bcm2835)

- **Missing Waveshare library**
  - Make sure the waveshare_epd directory exists and contains driver files
  - Install it if needed:
    ```bash
    git clone https://github.com/waveshare/e-Paper.git waveshare_repo
    mkdir -p waveshare_epd
    cp -r waveshare_repo/RaspberryPi_JetsonNano/python/lib/waveshare_epd/*.py waveshare_epd/
    ```

- **Wrong display model**
  - Try the check_model.py script to find which model works with your hardware

### 2. Display hanging during initialization

**Possible solutions:**

- **Reset the HAT**
  - Disconnect power
  - Wait 30 seconds
  - Reconnect power and try again

- **Check the BUSY pin**
  - If the BUSY pin is stuck, the display won't initialize
  - Run simple_test.py to see the BUSY pin status

- **Try a different model**
  - Some displays are slightly different than their labeled model
  - Try check_model.py to test different models

### 3. Error messages

- **"No module named 'waveshare_epd'"**
  - The Waveshare library is not installed or not in the Python path
  - Follow the installation instructions above

- **"Error initializing display"**
  - Check hardware connections
  - Try a different model driver
  - Check power supply

## Hardware Verification

1. **Visual inspection**
   - Look for LEDs on the HAT (if any) to confirm power
   - Check all connections and ribbon cables
   - Inspect for any physical damage

2. **GPIO test**
   - Run simple_test.py to verify GPIO communication

3. **SPI test**
   - Run simple_test.py to verify SPI communication

## Additional Tips

- **Patience**: E-ink displays are slow to update (several seconds)
- **Temperature**: E-ink displays can behave differently in extreme temperatures
- **Rest period**: Some displays need a rest period between operations
- **Fresh start**: Sometimes a full reboot helps with initialization issues