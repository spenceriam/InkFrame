#!/bin/bash
# Fix Waveshare EPD library installation

set -e

# ANSI colors
GREEN='\033[0;32m'
BLUE='\033[0;34m'
RED='\033[0;31m'
NC='\033[0m' # No Color

echo -e "${BLUE}Fixing Waveshare EPD library installation...${NC}"

# Check if running as root
if [ "$EUID" -ne 0 ]; then
  echo -e "${RED}Please run as root (use sudo)${NC}"
  exit 1
fi

# Get the directory where the script is located
SCRIPT_DIR=$(cd "$(dirname "${BASH_SOURCE[0]}")" &>/dev/null && pwd)
cd "$SCRIPT_DIR"

# Remove old installation if exists
if [ -d "waveshare_epd" ]; then
  echo -e "${GREEN}Removing old waveshare_epd directory...${NC}"
  rm -rf waveshare_epd
fi

echo -e "${GREEN}Cloning Waveshare e-Paper library...${NC}"
git clone https://github.com/waveshare/e-Paper.git waveshare_repo

echo -e "${GREEN}Installing Waveshare library into Python environment...${NC}"
# Create waveshare_epd directory
mkdir -p waveshare_epd

# Copy the required Python files
cp -r waveshare_repo/RaspberryPi_JetsonNano/python/lib/waveshare_epd/*.py waveshare_epd/

# Create __init__.py to make it a proper Python package
touch waveshare_epd/__init__.py

# Also install in the virtual environment's site-packages
if [ -d "venv" ]; then
  source venv/bin/activate
  
  # Find the site-packages directory
  SITE_PACKAGES=$(python -c "import site; print(site.getsitepackages()[0])")
  
  # Copy waveshare_epd to site-packages
  echo -e "${GREEN}Installing to virtual environment: $SITE_PACKAGES${NC}"
  cp -r waveshare_epd "$SITE_PACKAGES/"
  
  # Also try installing dependencies
  pip install RPi.GPIO spidev
fi

# Clean up
rm -rf waveshare_repo

# Set permissions
chown -R pi:pi waveshare_epd

echo -e "${GREEN}Testing Python import...${NC}"
# Test if we can import the modules
python3 -c "
try:
    import waveshare_epd.epd7in5_V2
    print('✓ Successfully imported epd7in5_V2')
except ImportError as e:
    print('✗ Failed to import epd7in5_V2:', e)

try:
    import waveshare_epd.epd7in3f
    print('✓ Successfully imported epd7in3f')
except ImportError as e:
    print('✗ Failed to import epd7in3f:', e)
"

echo -e "${BLUE}=========================================${NC}"
echo -e "${GREEN}Waveshare library fix complete!${NC}"
echo -e "${BLUE}=========================================${NC}"
echo
echo "Now restart the display service:"
echo -e "${GREEN}sudo systemctl restart inkframe-display.service${NC}"