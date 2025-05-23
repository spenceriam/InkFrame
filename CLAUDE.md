# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Project Overview

InkFrame is a digital photo frame application designed for Raspberry Pi Zero W with a Waveshare 7.5" e-ink display. It provides a web interface for photo management and displays photos with a status bar showing time and weather information.

## Current Status

The project is in active development with the following components implemented:
- Core architecture and file structure
- E-ink display driver with grayscale and diagnostic support
- Image processing utilities with dithering and optimization
- Photo management system with multiple display modes
- Weather client for OpenWeatherMap integration
- Configuration management system

Troubleshooting tools are available for hardware integration:
- `simple_test.py` - Tests GPIO and SPI without initializing the display
- `basic_test.py` - Minimal test for display initialization and clearing
- `check_model.py` - Tests different display models for compatibility
- `official_test.py` - Adapted from Waveshare's official examples
- `troubleshooting.md` - Comprehensive guide for hardware issues

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

### Hardware Testing

```bash
# Test GPIO and SPI communication
python simple_test.py

# Test basic display functionality
python basic_test.py

# Find compatible display model
python check_model.py

# Run official Waveshare test
python official_test.py
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

### Hardware Integration

When deploying to Raspberry Pi hardware:
- Ensure the correct Waveshare library is installed in the waveshare_epd directory
- Hardware setup requires GPIO and SPI configuration
- Testing should follow a systematic approach: GPIO/SPI → basic connectivity → full functionality
- Consult troubleshooting.md for detailed hardware debugging steps

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
- Hardware connections must be precise; check GPIO pin alignment carefully
- Always ensure SPI interface is enabled (via raspi-config)
- Display driver selection must match the exact model variant
- Some displays require more power during initialization phase

### Resource Constraints

When developing features, remember the Raspberry Pi Zero W has:
- Single 1GHz CPU core
- 512MB RAM

Optimize code to work within these constraints:
- Process images at upload time rather than display time
- Minimize memory-intensive operations
- Use efficient file formats (BMP works faster with e-ink)

### Development Workflow

When making changes to the codebase:
1. Implement the requested features or fixes
2. Update `changelog.md` with a summary of changes
3. Commit changes with a descriptive message
4. Push to GitHub so changes can be pulled on the InkFrame device

**IMPORTANT**: Always remember to:
- Update `changelog.md` before committing
- Use `git commit` with the Claude Code signature
- Push changes to the repository