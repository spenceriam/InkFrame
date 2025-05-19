# InkFrame

A minimal, elegant digital photo frame using a Raspberry Pi Zero W and Waveshare 7.5" e-ink display.

<p align="center">
  <img src="docs/images/preview.png" alt="InkFrame Preview" width="600"><br>
  <em>E-ink photo frame with status bar showing time and weather</em>
</p>

## Features

- **Beautiful E-ink Display**: Optimized grayscale images on a 7.5" Waveshare e-ink display
- **Auto-Cycling Photos**: Configurable rotation interval for changing displayed photos
- **Status Bar**: Shows current time and local weather information
- **Web Interface**: Simple browser-based management interface for photos and settings
- **Lightweight Design**: Optimized for Raspberry Pi Zero W's limited resources
- **Automatic Startup**: Launches on boot via systemd services
- **Weather Integration**: Real-time weather data via OpenWeatherMap API
- **Flexible Image Handling**: Supports JPG, PNG, BMP, and HEIC formats

## Hardware Requirements

- Raspberry Pi Zero W
- Waveshare 7.5" e-ink display with HAT
- microSD card (8GB+ recommended)
- Power supply for Raspberry Pi

## Architecture

InkFrame follows a modular design with these main components:

```
+-------------------------+        +-------------------------+
|                         |        |                         |
|    Display Component    |<------>|   Web UI Component     |
|    (Python/Pillow)      |        |   (Flask/JavaScript)   |
|                         |        |                         |
+-------------^-----------+        +-------------^-----------+
              |                                  |
              v                                  v
+-------------------------+        +-------------------------+
|                         |        |                         |
|  Image Processing Utils |        |    Weather Services    |
|  (Pillow/ImageMagick)   |        |  (OpenWeatherMap API)  |
|                         |        |                         |
+-------------------------+        +-------------------------+
              ^                                  ^
              |                                  |
              v                                  v
+-------------------------+        +-------------------------+
|                         |        |                         |
|   E-Ink Display Driver  |        |  Configuration Manager |
|   (Waveshare Library)   |        |   (JSON-based config)  |
|                         |        |                         |
+-------------------------+        +-------------------------+
```

## Quick Start

1. Flash Raspberry Pi OS Lite to your SD card
2. Configure WiFi and enable SSH, SPI
3. Connect the Waveshare e-ink HAT to your Pi
4. Clone this repository and run the installation script:

```bash
git clone https://github.com/yourusername/InkFrame.git
cd InkFrame
./install.sh
```

5. Access the web interface at `http://your-pi-ip:5000`
6. Upload photos and configure settings

## Documentation

For detailed instructions and documentation, see:

- [Installation Guide](docs/installation.md)
- [User Manual](docs/user_manual.md)
- [API Documentation](docs/api.md)
- [Development Guide](docs/development.md)

## Weather Setup

InkFrame uses OpenWeatherMap for weather data. You'll need to:

1. Sign up for a free API key at [OpenWeatherMap](https://openweathermap.org/api)
2. Enter your API key and location in the web interface settings

## Development

For local development on non-Raspberry Pi systems:

1. Clone the repository
2. Install dependencies: `pip install -r requirements.txt`
3. Run the simulation test: `python tests/test_simulation.py`

The simulation mode creates display outputs in the `/simulation` directory so you can see how images would appear on the e-ink display.

## Customization

InkFrame is designed to be customizable. You can:

- Modify the web interface appearance by editing the CSS
- Adjust image processing parameters in the configuration
- Customize the status bar layout

## Contributing

Contributions are welcome! Please feel free to submit a Pull Request.

## License

MIT

## Acknowledgments

- [Waveshare](https://www.waveshare.com/) for their e-Paper display and library
- [Flask](https://flask.palletsprojects.com/) for the web framework
- [Pillow](https://python-pillow.org/) for image processing
- [OpenWeatherMap](https://openweathermap.org/) for weather data API