# InkFrame Installation Guide

This guide covers the complete installation process for InkFrame on a Raspberry Pi Zero W with a Waveshare e-ink display.

## Hardware Requirements

- Raspberry Pi Zero W
- Waveshare e-ink display with HAT (choose one):
  - 7.5" black and white/grayscale e-ink display
  - 7.3" ACeP 7-color e-ink display
- MicroSD card (8GB or larger recommended)
- Power supply for Raspberry Pi (5V/2.5A recommended)
- Computer with SD card reader for initial setup

## Preparing the Raspberry Pi

### Step 1: Install Raspberry Pi OS

1. Download the Raspberry Pi Imager from [raspberrypi.org](https://www.raspberrypi.org/software/)
2. Insert your microSD card into your computer
3. Open Raspberry Pi Imager
4. Click "CHOOSE OS" and select "Raspberry Pi OS Lite (32-bit)" for a minimal installation
5. Click "CHOOSE STORAGE" and select your microSD card
6. Click the gear icon (⚙️) to access advanced options:
   - Enable SSH
   - Configure WiFi (enter your network name and password)
   - Set hostname (e.g., inkframe)
   - Set username and password
   - Set locale settings
7. Click "SAVE" to apply these settings
8. Click "WRITE" to flash the OS to the SD card
9. Wait for the process to complete, then eject the SD card

### Step 2: Connect the Hardware

1. Insert the microSD card into the Raspberry Pi Zero W
2. Connect the Waveshare e-ink HAT to the Raspberry Pi:
   - Carefully align the GPIO pins and gently press the HAT onto the Raspberry Pi
   - The HAT should sit firmly on the Raspberry Pi
3. Connect the power supply to the Raspberry Pi

### Step 3: First Boot and Connection

1. Power on the Raspberry Pi by connecting the power supply
2. Wait a few minutes for the initial boot process to complete
3. From your computer, open a terminal/command prompt
4. Connect to your Raspberry Pi via SSH:
   ```
   ssh pi@inkframe.local
   ```
   (If you set a different hostname, use that instead of "inkframe")
5. Enter your password when prompted

## Installing InkFrame

### Step 1: Clone the Repository

1. Update your system packages:
   ```
   sudo apt update
   sudo apt upgrade -y
   ```

2. Install Git:
   ```
   sudo apt install git -y
   ```

3. Clone the InkFrame repository:
   ```
   git clone https://github.com/yourusername/InkFrame.git
   cd InkFrame
   ```

### Step 2: Run the Installation Script

1. Make the installation script executable:
   ```
   chmod +x install.sh
   ```

2. Run the installation script:
   ```
   sudo ./install.sh
   ```

3. The script will:
   - Install required system packages
   - Set up a Python virtual environment
   - Install Python dependencies
   - Configure the Waveshare e-ink library
   - Create and enable system services
   - Configure Nginx as a reverse proxy
   - Enable the SPI interface

4. Once the installation is complete, restart your Raspberry Pi:
   ```
   sudo reboot
   ```

## Verifying the Installation

1. After the Raspberry Pi reboots, reconnect via SSH:
   ```
   ssh pi@inkframe.local
   ```

2. Check the status of the InkFrame services:
   ```
   sudo systemctl status inkframe-web.service
   sudo systemctl status inkframe-display.service
   ```

   Both services should be active and running.

3. Access the web interface by entering the Raspberry Pi's IP address in a web browser:
   ```
   http://inkframe.local
   ```
   or
   ```
   http://[IP_ADDRESS]
   ```

## Troubleshooting

### SPI Interface Issues

If the e-ink display is not working properly, verify that SPI is enabled:

```
lsmod | grep spi
```

You should see `spi_bcm2835` in the output. If not, enable SPI:

1. Run `sudo raspi-config`
2. Select "Interface Options"
3. Select "SPI"
4. Select "Yes" to enable the SPI interface
5. Reboot the Raspberry Pi

### Setting Up for 7.3 inch ACeP 7-Color Display

If you're using the 7.3 inch ACeP 7-color display instead of the 7.5 inch B&W display:

1. Determine your exact display model:
   ```
   cd ~/InkFrame
   python tests/hardware/check_model.py
   ```
   This script will test different display models and identify which one works with your hardware.

2. Run the color-specific test script:
   ```
   python tests/color/color_test.py
   ```
   This will display a color test pattern showing all 7 available colors.

3. Update your configuration:
   ```
   nano config/default_config.json
   ```
   
   Add these settings in the "display" section:
   ```json
   "display_type": "7in3f",
   "color_mode": "color"
   ```
   
   Save and exit (Ctrl+O, Enter, Ctrl+X).

4. Important notes for 7.3 inch ACeP display:
   - Refresh time is approximately 35 seconds (vs. 1-2 seconds for B&W)
   - Full 7-color support requires specific RGB values (see models.txt)
   - Higher power consumption during refresh
   - To avoid damaging the display, set reasonable refresh intervals (5+ minutes)

### Service Issues

If either service is not running:

```
sudo systemctl restart inkframe-web.service
sudo systemctl restart inkframe-display.service
```

Check the logs for errors:

```
sudo journalctl -u inkframe-web.service
sudo journalctl -u inkframe-display.service
```

### Permission Issues

If you encounter permission errors:

```
sudo chown -R pi:pi /home/pi/InkFrame
```

## Next Steps

Once installation is complete, refer to the [User Manual](user_manual.md) for instructions on using InkFrame.

## Updating InkFrame

To update InkFrame to the latest version:

1. Navigate to the InkFrame directory:
   ```
   cd ~/InkFrame
   ```

2. Pull the latest changes:
   ```
   git pull
   ```

3. Run the installation script again:
   ```
   sudo ./install.sh
   ```

4. Restart the services:
   ```
   sudo systemctl restart inkframe-web.service
   sudo systemctl restart inkframe-display.service
   ```