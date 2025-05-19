# InkFrame Development Guide

This document provides information for developers who want to understand, modify, or contribute to the InkFrame project.

## Project Structure

The InkFrame codebase is organized as follows:

```
InkFrame/
├── config/                  # Configuration files
│   └── default_config.json  # Default configuration template
├── docs/                    # Documentation
├── src/                     # Source code
│   ├── display/             # Display-related modules
│   │   ├── eink_driver.py   # E-ink display driver
│   │   └── photo_manager.py # Photo management and display
│   ├── utils/               # Utility modules
│   │   ├── config_manager.py # Configuration management
│   │   └── image_processor.py # Image processing utilities
│   ├── weather/             # Weather-related modules
│   │   └── weather_client.py # OpenWeatherMap client
│   ├── web/                 # Web interface
│   │   └── app.py           # Flask application
│   └── main.py              # Main entry point
├── static/                  # Static web assets
│   ├── css/                 # CSS stylesheets
│   ├── js/                  # JavaScript files
│   ├── images/              # Image assets and photos
│   └── templates/           # HTML templates
├── tests/                   # Test scripts
├── .gitignore               # Git ignore file
├── install.sh               # Installation script
├── README.md                # Project readme
└── requirements.txt         # Python dependencies
```

## Development Environment Setup

### Local Development (Non-Raspberry Pi)

You can develop and test most of InkFrame's functionality on any computer, even without a Raspberry Pi or e-ink display.

1. Clone the repository:
   ```bash
   git clone https://github.com/yourusername/InkFrame.git
   cd InkFrame
   ```

2. Create a virtual environment:
   ```bash
   python -m venv venv
   source venv/bin/activate  # On Windows: venv\Scripts\activate
   ```

3. Install dependencies:
   ```bash
   pip install -r requirements.txt
   ```

4. Run the simulation test:
   ```bash
   python tests/test_simulation.py
   ```

5. Start the web interface in development mode:
   ```bash
   python src/web/app.py
   ```

   The web interface will be available at http://localhost:5000

### Raspberry Pi Development Environment

For development directly on the Raspberry Pi:

1. Install the required packages:
   ```bash
   sudo apt update
   sudo apt install -y python3-pip python3-venv git
   ```

2. Follow the same steps as for local development above.

3. For testing with the actual e-ink display, ensure SPI is enabled:
   ```bash
   sudo raspi-config
   # Navigate to Interface Options > SPI > Yes
   ```

## Key Components

### E-Ink Display Driver

The `eink_driver.py` module handles communication with the Waveshare e-ink display. It:
- Initializes the display hardware
- Provides methods for displaying images
- Handles conversion of images to the format required by the display
- Includes a simulation mode for development on non-Raspberry Pi systems

### Photo Manager

The `photo_manager.py` module manages the photo display cycle:
- Selects random photos from the library
- Creates a composite image with the status bar
- Handles the display refresh timing
- Coordinates with the weather client for current data

### Image Processor

The `image_processor.py` module handles image processing:
- Resizes images to fit the display
- Converts images to grayscale or black and white
- Applies dithering for better e-ink appearance
- Generates thumbnails for the web interface
- Handles HEIC conversion using ImageMagick

### Web Interface

The `app.py` module provides a Flask web application with:
- RESTful API endpoints for photo and configuration management
- Photo upload and management interface
- Configuration settings interface
- System status information

### Configuration Manager

The `config_manager.py` module handles:
- Loading and saving configuration from JSON files
- Providing default configuration values
- Validating configuration data

### Weather Client

The `weather_client.py` module:
- Retrieves weather data from OpenWeatherMap
- Caches data to reduce API calls
- Formats weather information for display

## Simulation Mode

To facilitate development without hardware, InkFrame includes a simulation mode:

- When the Waveshare library is not available, the display driver automatically switches to simulation mode
- Instead of updating the physical display, it saves images to the `simulation` directory
- This allows you to see what would be displayed on the e-ink screen

## Customization Guide

### Changing the Display Size

If you're using a different e-ink display size:

1. Update the dimensions in `eink_driver.py`:
   ```python
   self.width = 800  # Change to your display width
   self.height = 480  # Change to your display height
   ```

2. Update the configuration in `default_config.json`:
   ```json
   "photos": {
     "max_width": 800,  // Change to your display width
     "max_height": 440  // Change to display height minus status bar
   }
   ```

3. If using a different Waveshare model, update the import in `eink_driver.py`:
   ```python
   from waveshare_epd import epd5in83_V2 as epd  # Change to your model
   ```

### Modifying the Web Interface

To customize the web interface:

1. Edit the HTML templates in `static/templates/`
2. Modify the CSS in `static/css/styles.css`
3. Update JavaScript functionality in `static/js/app.js`

### Adding New Features

To add new features:

1. Identify the appropriate module for your feature
2. Add your functionality
3. Update the API in `app.py` if needed
4. Update the web interface if applicable
5. Add appropriate documentation

## Testing

The `tests/test_simulation.py` script provides basic testing functionality:
- Tests configuration loading and saving
- Tests the e-ink display driver in simulation mode
- Tests the photo manager's ability to select and display photos

To run the tests:
```bash
python tests/test_simulation.py
```

## Common Challenges

### Raspberry Pi Resource Constraints

The Raspberry Pi Zero W has limited resources:
- Single 1GHz CPU core
- 512MB RAM

To work within these constraints:
- Minimize image processing at runtime
- Pre-process images upon upload
- Avoid heavy libraries or frameworks
- Use efficient file formats (BMP is faster for e-ink displays)

### E-Ink Display Characteristics

E-ink displays have specific characteristics:
- Slow refresh rates (several seconds)
- Limited grayscale capability (typically 16 levels)
- Tendency to show ghosting (remnants of previous images)

Techniques to optimize for e-ink:
- Use dithering for better grayscale appearance
- Refresh the entire display periodically to reduce ghosting
- Keep display updates to a minimum

## Contributing

We welcome contributions to InkFrame! To contribute:

1. Fork the repository
2. Create a feature branch: `git checkout -b feature/your-feature-name`
3. Make your changes
4. Commit your changes: `git commit -m "Add feature: your feature description"`
5. Push to your fork: `git push origin feature/your-feature-name`
6. Create a pull request

Please include:
- Clear description of the changes
- Any necessary documentation updates
- Test results if applicable

## Additional Resources

- [Waveshare e-Paper Wiki](https://www.waveshare.com/wiki/7.5inch_e-Paper_HAT)
- [Flask Documentation](https://flask.palletsprojects.com/)
- [Pillow Documentation](https://pillow.readthedocs.io/)
- [OpenWeatherMap API Documentation](https://openweathermap.org/api)