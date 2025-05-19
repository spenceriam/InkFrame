# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Project Overview

InkFrame is a digital photo frame application designed for Raspberry Pi Zero W with a Waveshare 7.5" e-ink display. It provides a web interface for photo management and displays photos with a status bar showing time and weather information.

## Architecture

The project follows a modular architecture:

- **Display Component**: Manages the e-ink display and photo cycle
- **Web UI Component**: Flask-based interface for photo management and settings
- **Image Processing**: Utilities for optimizing photos for e-ink display
- **Weather Services**: OpenWeatherMap API integration
- **Configuration Manager**: Handles persistent app settings

## Key Commands

### Setup and Installation

```bash
# Create a virtual environment
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt
```

### Running the Application

```bash
# Run the full application (both web and display components)
python run.py

# Run only the web interface
python run.py --web-only --port 5000

# Run only the display component
python run.py --display-only

# Run with debug mode
python run.py --debug
```

### Running Tests

```bash
# Run simulation test (works on non-Raspberry Pi systems)
python tests/test_simulation.py
```

## Development Notes

### Simulation Mode

For development on non-Raspberry Pi systems, InkFrame provides a simulation mode that:
- Automatically activates when Waveshare libraries aren't available
- Saves display output to the `simulation` directory
- Allows testing of most functionality without hardware

### Project Structure Highlights

- `src/display/eink_driver.py`: E-ink display interface, handles rendering to hardware
- `src/display/photo_manager.py`: Controls photo selection and display cycle
- `src/utils/image_processor.py`: Image optimization for e-ink display
- `src/web/app.py`: Flask web application for photo management
- `src/weather/weather_client.py`: Handles weather data retrieval and formatting
- `src/utils/config_manager.py`: Manages persistent configuration

### E-Ink Display Considerations

- E-ink has slow refresh rates (several seconds)
- Limited grayscale capability (typically 16 levels)
- Use dithering for better image appearance
- Keep display updates minimal to conserve battery and improve performance

### Resource Constraints

When developing features, remember the Raspberry Pi Zero W has:
- Single 1GHz CPU core
- 512MB RAM

Optimize code to work within these constraints:
- Process images at upload time rather than display time
- Minimize memory-intensive operations
- Use efficient file formats (BMP works faster with e-ink)