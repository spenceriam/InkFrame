# AGENTS.md

This file provides guidance to AI agents when working with code in this repository.

## Project Overview

InkFrame is a digital photo frame application designed for Raspberry Pi Zero W with Waveshare e-ink displays. It provides a web interface for photo management and displays photos with a status bar showing time, date, and weather information.

## Current Version

Version: 1.1.0

## Agent Guidelines

### Code Organization

The project follows a modular architecture:

- **src/display/**: E-ink display management
  - `eink_driver.py`: Hardware abstraction for the display
  - `photo_manager.py`: Photo selection and display cycle logic

- **src/web/**: Web interface
  - `app.py`: Flask application and API endpoints

- **src/weather/**: Weather data integration
  - `weather_client.py`: Weather.gov API client

- **src/utils/**: Shared utilities
  - `image_processor.py`: Image optimization for e-ink
  - `config_manager.py`: Configuration persistence

- **tests/**: All test files organized by purpose
  - `test_simulation.py`: Simulation mode tests (works on any system)
  - `test_*.py`: Unit and integration tests
  - `hardware/`: Hardware diagnostic and testing scripts
  - `color/`: Color display specific tests

### Development Principles

1. **Resource Constraints**: Raspberry Pi Zero W has single 1GHz CPU and 512MB RAM
   - Process images at upload time, not display time
   - Use efficient file formats (BMP works faster with e-ink)
   - Minimize memory-intensive operations

2. **E-Ink Display Considerations**
   - Slow refresh rates (several seconds)
   - Limited grayscale capability (16 levels for monochrome, 7 colors for ACeP)
   - Use dithering for better image appearance
   - Minimize display updates to conserve battery

3. **Version Management**
   - Follow semantic versioning (MAJOR.MINOR.PATCH)
   - Update version in `src/version.py`
   - Update AGENTS.md with version information
   - Document breaking changes in version updates

4. **Testing Workflow**
   - Use simulation mode for non-RPi development
   - Test on actual hardware before deploying
   - Follow hardware testing sequence: GPIO/SPI → basic connectivity → full functionality
   - All test files should be in the `tests/` directory, organized by purpose

### Service Status Reporting

The display service has two status flags:
- `running`: Whether the display cycle is actively running
- `started`: Whether the service has been initialized (even if not actively cycling)

Both flags should be checked to determine the true service state.

### Weather Integration

The application uses the weather.gov API:
- Location is determined via IP geolocation or config
- Falls back to McHenry, IL if detection fails
- API requires User-Agent header with contact info
- Returns temperature, conditions, and current date
- Only covers US locations

### Test Directory Organization

All test files are organized in the `tests/` directory:

```
tests/
├── README.md                           # Test documentation
├── test_simulation.py                 # Simulation mode tests
├── test_display.py                    # Display component tests
├── test_photo_manager.py              # Photo manager unit tests
├── test_full_display.py               # End-to-end display tests
├── test_color_pipeline.py             # Color processing pipeline tests
├── test_display_colors.py             # Display color rendering tests
├── test_our_display.py                # Custom display logic tests
├── test_display_direct.py             # Direct display driver tests
├── test_save_canvas.py                # Canvas saving tests
├── test_weather_api.py                # Weather API integration tests
├── hardware/                          # Hardware diagnostic scripts
│   ├── simple_test.py                # GPIO and SPI basic test
│   ├── basic_test.py                 # Minimal display initialization test
│   ├── official_test.py              # Waveshare official test adaptation
│   ├── check_model.py                # Display model compatibility checker
│   ├── lgpio_test.py                 # lgpio library test
│   └── lgpio_reset_test.py           # GPIO reset test
└── color/                             # Color display specific tests
    └── color_test.py                 # ACeP 7-color display test
```

**When writing tests:**
- All test files must be in the `tests/` directory
- Hardware-specific tests go in `tests/hardware/`
- Color-specific tests go in `tests/color/`
- Unit tests for components should be named `test_<component>.py`
- All tests should include clear docstrings explaining their purpose
- Tests should be runnable independently

### Common Tasks

#### Adding a New Feature

1. Implement the feature in the appropriate module
2. Update configuration in `src/utils/config_manager.py` if needed
3. Add API endpoints in `src/web/app.py` if web interface is needed
4. Write tests in the appropriate `tests/` subdirectory
5. Update `src/version.py` for version bump
6. Update this AGENTS.md file
7. Update `changelog.md`
8. Commit with descriptive message

#### Debugging Display Issues

1. Check logs for error messages
2. Run hardware tests in order:
   - `tests/hardware/simple_test.py`: GPIO and SPI
   - `tests/hardware/check_model.py`: Display model detection
   - `tests/hardware/basic_test.py`: Display initialization
   - `tests/hardware/official_test.py`: Full compatibility check
3. Consult `troubleshooting.md` for detailed steps

#### Updating Weather Integration

1. Modify `src/weather/weather_client.py`
2. Ensure location detection has proper fallbacks
3. Test with different locations
4. Verify API response format changes
5. Run `tests/test_weather_api.py` to verify changes

#### Moving or Organizing Test Files

1. All test files must be in `tests/` directory
2. Hardware diagnostic scripts go in `tests/hardware/`
3. Color-specific tests go in `tests/color/`
4. Update all documentation that references test paths
5. Update this AGENTS.md file with new locations
6. Verify imports and references are updated

### Branch Naming Convention

- `feature/` - New features
- `bugfix/` - Bug fixes
- `hotfix/` - Critical fixes for production
- `refactor/` - Code refactoring

### Commit Message Format

Follow conventional commits:
- `feat:` - New feature
- `fix:` - Bug fix
- `docs:` - Documentation changes
- `refactor:` - Code refactoring
- `test:` - Test changes
- `chore:` - Maintenance tasks
- `test:organize:` - Test file reorganization

### Code Review Checklist

Before submitting changes:
- [ ] Code follows project structure
- [ ] No resource leaks (file handles, threads, etc.)
- [ ] Error handling is comprehensive
- [ ] Logging is appropriate
- [ ] Version has been updated if needed
- [ ] AGENTS.md has been updated
- [ ] Tests are in correct subdirectory
- [ ] Documentation references updated for test paths
- [ ] Changes tested in simulation mode
- [ ] Documentation updated

## Project Structure

```
inkframe/
├── src/
│   ├── display/
│   │   ├── eink_driver.py
│   │   └── photo_manager.py
│   ├── web/
│   │   └── app.py
│   ├── weather/
│   │   └── weather_client.py
│   ├── utils/
│   │   ├── config_manager.py
│   │   └── image_processor.py
│   └── version.py
├── tests/
│   ├── README.md
│   ├── test_simulation.py
│   ├── test_display.py
│   ├── test_photo_manager.py
│   ├── test_full_display.py
│   ├── test_color_pipeline.py
│   ├── test_display_colors.py
│   ├── test_our_display.py
│   ├── test_display_direct.py
│   ├── test_save_canvas.py
│   ├── test_weather_api.py
│   ├── hardware/
│   │   ├── simple_test.py
│   │   ├── basic_test.py
│   │   ├── official_test.py
│   │   ├── check_model.py
│   │   ├── lgpio_test.py
│   │   └── lgpio_reset_test.py
│   └── color/
│       └── color_test.py
├── templates/
│   └── index.html
├── static/
│   └── (CSS, JS, images)
├── photos/
│   └── (uploaded photos)
├── docs/
│   └── (documentation)
├── config/
│   └── (configuration files)
├── run.py
├── requirements.txt
├── AGENTS.md
├── CLAUDE.md
├── README.md
└── changelog.md
```

## API Reference

### Display Service Status

GET `/api/status`

Returns:
```json
{
  "display": {
    "running": true,
    "started": true,
    "photo_count": 10,
    "current_index": 3,
    "display_mode": "sequential",
    "cycle_interval": 300,
    "weather_enabled": true
  },
  "weather": {
    "available": true,
    "temperature": "72°F",
    "condition": "Partly Cloudy",
    "date": "June 15, 2025"
  },
  "version": "1.1.0",
  "timestamp": "2025-06-15T14:30:00"
}
```

### Photo Management

- `GET /api/photos` - List all photos
- `POST /api/photos/upload` - Upload a new photo
- `DELETE /api/photos/<filename>` - Delete a photo
- `GET /api/photos/<filename>` - Serve a photo file

### Configuration

- `GET /api/config` - Get all configuration
- `POST /api/config` - Update configuration

### Display Control

- `POST /api/display/refresh` - Force display refresh

## Hardware Testing Commands

```bash
# Test GPIO and SPI communication
python tests/hardware/simple_test.py

# Test basic display functionality
python tests/hardware/basic_test.py

# Find compatible display model
python tests/hardware/check_model.py

# Run official Waveshare test
python tests/hardware/official_test.py

# Test lgpio library
python tests/hardware/lgpio_test.py

# Run full simulation test
python tests/test_simulation.py

# Run color display test
python tests/color/color_test.py
```

See `tests/README.md` for comprehensive testing documentation.

## Version History

### v1.1.0 (Current)
- Migrated from OpenWeatherMap to weather.gov API
- Added IP-based geolocation for weather
- Added current date display to status bar
- Fixed display service status reporting
- Added version display in ghost text
- Created AGENTS.md for AI agent guidance
- Reorganized test files into `tests/` directory structure
- Separated hardware tests into `tests/hardware/`
- Separated color tests into `tests/color/`
- Updated all documentation for new test paths

### v1.0.0
- Initial release
- Basic photo frame functionality
- OpenWeatherMap integration
- Web interface for photo management