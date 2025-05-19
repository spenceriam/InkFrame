#!/bin/bash
# InkFrame installation script
# This script installs and configures InkFrame on a Raspberry Pi Zero W

set -e

# ANSI colors
GREEN='\033[0;32m'
BLUE='\033[0;34m'
RED='\033[0;31m'
NC='\033[0m' # No Color

echo -e "${BLUE}=========================================${NC}"
echo -e "${BLUE}  InkFrame Installation Script${NC}"
echo -e "${BLUE}  E-Ink Photo Frame for Raspberry Pi${NC}"
echo -e "${BLUE}=========================================${NC}"
echo

# Check if running as root
if [ "$EUID" -ne 0 ]; then
  echo -e "${RED}Please run as root (use sudo)${NC}"
  exit 1
fi

# Get the directory where the script is located
SCRIPT_DIR=$(cd "$(dirname "${BASH_SOURCE[0]}")" &>/dev/null && pwd)
cd "$SCRIPT_DIR"

echo -e "${GREEN}Updating system packages...${NC}"
apt-get update
apt-get upgrade -y

echo -e "${GREEN}Installing required packages...${NC}"
apt-get install -y \
  python3 \
  python3-pip \
  python3-venv \
  python3-dev \
  libopenjp2-7 \
  libtiff5 \
  imagemagick \
  git \
  nginx

echo -e "${GREEN}Setting up Python virtual environment...${NC}"
python3 -m venv venv
source venv/bin/activate

echo -e "${GREEN}Installing Python dependencies...${NC}"
pip install --upgrade pip
pip install \
  flask \
  pillow \
  requests \
  RPi.GPIO \
  spidev \
  pytz \
  gunicorn

echo -e "${GREEN}Installing Waveshare e-Paper library...${NC}"
if [ ! -d "waveshare_epd" ]; then
  # Clone the Waveshare e-Paper library repository
  git clone https://github.com/waveshare/e-Paper.git waveshare_repo

  # Copy the required Python files
  mkdir -p waveshare_epd
  cp -r waveshare_repo/RaspberryPi_JetsonNano/python/lib/waveshare_epd/*.py waveshare_epd/
  
  # Clean up
  rm -rf waveshare_repo
fi

echo -e "${GREEN}Creating directories...${NC}"
mkdir -p static/images/photos/thumbnails
mkdir -p static/images/photos/uploads
mkdir -p config
mkdir -p logs

echo -e "${GREEN}Setting permissions...${NC}"
chown -R pi:pi .
chmod +x src/web/app.py
chmod +x src/display/photo_manager.py

echo -e "${GREEN}Creating service files...${NC}"
# Create web service file
cat > /etc/systemd/system/inkframe-web.service << EOF
[Unit]
Description=InkFrame Web Interface
After=network.target

[Service]
User=pi
WorkingDirectory=${SCRIPT_DIR}
ExecStart=${SCRIPT_DIR}/venv/bin/gunicorn --workers 1 --bind 0.0.0.0:5000 src.web.app:app
Restart=always
RestartSec=5
Environment=PYTHONPATH=${SCRIPT_DIR}

[Install]
WantedBy=multi-user.target
EOF

# Create display service file
cat > /etc/systemd/system/inkframe-display.service << EOF
[Unit]
Description=InkFrame Photo Display
After=network.target

[Service]
User=pi
WorkingDirectory=${SCRIPT_DIR}
ExecStart=${SCRIPT_DIR}/venv/bin/python3 ${SCRIPT_DIR}/src/display/photo_manager.py
Restart=always
RestartSec=5
Environment=PYTHONPATH=${SCRIPT_DIR}

[Install]
WantedBy=multi-user.target
EOF

echo -e "${GREEN}Enabling SPI interface...${NC}"
if ! grep -q "dtparam=spi=on" /boot/config.txt; then
  echo "dtparam=spi=on" >> /boot/config.txt
  echo "SPI interface enabled. A reboot will be required."
else
  echo "SPI interface already enabled."
fi

echo -e "${GREEN}Enabling and starting services...${NC}"
systemctl daemon-reload
systemctl enable inkframe-web.service
systemctl enable inkframe-display.service
systemctl start inkframe-web.service
systemctl start inkframe-display.service

# Set up Nginx as a reverse proxy (optional)
echo -e "${GREEN}Configuring Nginx as reverse proxy...${NC}"
cat > /etc/nginx/sites-available/inkframe << EOF
server {
    listen 80;
    server_name _;

    location / {
        proxy_pass http://127.0.0.1:5000;
        proxy_set_header Host \$host;
        proxy_set_header X-Real-IP \$remote_addr;
        proxy_set_header X-Forwarded-For \$proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto \$scheme;
    }

    client_max_body_size 16M;
}
EOF

# Enable the Nginx site
ln -sf /etc/nginx/sites-available/inkframe /etc/nginx/sites-enabled/
rm -f /etc/nginx/sites-enabled/default
systemctl restart nginx

# Get IP address for user reference
IP_ADDRESS=$(hostname -I | cut -d' ' -f1)

echo -e "${BLUE}=========================================${NC}"
echo -e "${GREEN}Installation complete!${NC}"
echo -e "${BLUE}=========================================${NC}"
echo
echo -e "You can access the InkFrame web interface at:"
echo -e "${GREEN}http://$IP_ADDRESS/${NC}"
echo
echo -e "Default configuration:"
echo -e "- Web interface port: 5000 (via Nginx on port 80)"
echo -e "- Photo directory: ${SCRIPT_DIR}/static/images/photos"
echo -e "- Config file: ${SCRIPT_DIR}/config/config.json"
echo
echo -e "A reboot is recommended to ensure all changes take effect."
echo -e "Run ${GREEN}sudo reboot${NC} to restart your Raspberry Pi."
echo