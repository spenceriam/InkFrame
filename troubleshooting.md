# E-Ink Display Troubleshooting Guide

This guide is designed to help troubleshoot issues with the Waveshare e-ink displays used in the InkFrame project. It covers both the 7.5" black and white/grayscale display and the 7.3" ACeP 7-color display.

## Test Scripts

We've provided several test scripts to help diagnose issues:

1. **simple_test.py** - Tests GPIO and SPI communication without initializing the display
2. **basic_test.py** - A minimal test that only tries to initialize and clear the display
3. **check_model.py** - Tests different display models to find which one works with your hardware
4. **official_test.py** - An adapted version of the official Waveshare test script
5. **test_display.py** - A more detailed test that includes a visual pattern
6. **color_test.py** - A test script specifically for the 7.3" ACeP 7-color display

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

## 7.3 inch ACeP 7-Color Display Specific Issues

The 7.3" ACeP display has some unique characteristics that can cause issues:

### 1. Very long refresh times

**Issue**: The display takes 30-40 seconds to refresh, which may appear as if it's frozen or not working.

**Solution**: Be patient and wait the full refresh cycle. The ACeP refresh process goes through several stages including flashing different colors before settling on the final image.

### 2. Color reproduction problems

**Issue**: Colors don't match what was expected or look faded/incorrect.

**Solutions**:
- Use exact RGB values specified for the 7 available colors (see models.txt)
- Ensure your images have high contrast
- The display itself has limited color fidelity - images may not match the source exactly
- Make sure you're using `color_mode: "color"` in your config

### 3. Higher power consumption

**Issue**: The 7.3" ACeP display uses significantly more power during refresh operations.

**Solutions**:
- Use a good quality 5V/2.5A power supply
- Set longer refresh intervals (5+ minutes recommended)
- Be prepared for higher power consumption compared to the B&W display

### 4. Display appears damaged after updates

**Issue**: Rushing multiple updates can potentially damage the display.

**Solution**:
- Wait at least 180 seconds between refresh operations
- Never interrupt a refresh cycle
- Update your config to have longer refresh intervals

## Additional Tips

- **Patience**: E-ink displays are slow to update (several seconds for B&W, up to 40 seconds for 7-color ACeP)
- **Temperature**: E-ink displays can behave differently in extreme temperatures
- **Rest period**: Some displays need a rest period between operations (especially the 7.3" ACeP display)
- **Fresh start**: Sometimes a full reboot helps with initialization issues