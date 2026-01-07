# AGENTS.md

This file provides guidance to AI agents and developers when working with code in this repository.

## Project Overview

InkFrame is a digital photo frame application designed for Raspberry Pi Zero W with Waveshare e-ink displays. It provides a web interface for photo management and displays photos with a status bar showing time, date, and weather information.

## Current Version

Version: 1.1.1 (v1.2.0 in development on `web-interface-improvements` branch)

## Version History

### v1.2.0 (In Development) - 2026-01-XX
- **NEW**: Interactive map-based location picker using Leaflet
- **NEW**: ZIP code and city name search for location geocoding
- **NEW**: Geocoding API endpoints (`/api/location/geocode`, `/api/location/reverse`)
- **NEW**: Stored coordinates (latitude/longitude) in config for precise location
- **REMOVED**: OpenWeatherMap API key field (obsolete since v1.1.0)
- **REMOVED**: Country code field (weather.gov is US-only)
- **IMPROVED**: Weather client prioritizes stored coordinates over geocoding
- **IMPROVED**: Auto-migration of legacy city/state configs to coordinates
- **UI**: Streamlined weather settings interface
- **DOCS**: Added `docs/web-interface-improve.md` implementation plan

### v1.1.1 (Current) - 2026-01-07
- **FIXED**: Missing ImageFont import in e-ink simulator
- **FIXED**: Orphaned code in test_simulation.py running at import time
- **FIXED**: Weather data format mismatch (nested 'current' dictionary access)
- **FIXED**: Dead DisplayMode.CLOCK and WEATHER references in CLI
- **FIXED**: Script imports from scripts/ subdirectories
- **ADDED**: /api/status endpoint with version info
- **CLEANED**: Duplicate code in test_simulation.py
- **DOCS**: Clarified API endpoint documentation

### v1.1.0 - 2025-06-15
- **BREAKING**: Migrated from OpenWeatherMap to weather.gov API
  - No API key required
  - US locations only (weather.gov limitation)
  - Automatic IP-based geolocation
  - Fallback to McHenry, IL coordinates
- **NEW**: Added current date display in status bar (Month Day, Year format)
- **NEW**: Added version number display in ghost text (bottom left)
- **NEW**: Created `src/version.py` with semantic versioning
- **FIXED**: Display service status reporting (added `_started` flag)
- **NEW**: E-ink display simulator for testing without hardware
- **NEW**: Comprehensive test organization
- **REORGANIZED**: All utility scripts moved to `scripts/` directory
  - `scripts/setup/` - Configuration and setup scripts
  - `scripts/utils/` - Utility and helper scripts
  - `scripts/photo/` - Photo processing scripts
  - `scripts/debug/` - Debugging and troubleshooting scripts
  - `scripts/fix/` - Bug fix and repair scripts

### v1.0.0 - Initial Release
- Basic photo frame functionality
- OpenWeatherMap integration
- Web interface for photo management
- Display management system

## Architecture

The project follows a modular architecture:

- **src/display/**: E-ink display management
  - `eink_driver.py`: Hardware abstraction for the display
  - `eink_simulator.py`: Display simulator for testing without hardware
  - `photo_manager.py`: Photo selection and display cycle logic

- **src/web/**: Web interface
  - `app.py`: Flask application and API endpoints

- **src/weather/**: Weather data integration
  - `weather_client.py`: Weather.gov API client (active)
  - `weather_client_free.py`: Legacy OpenWeatherMap free tier client (unused)
  - `weather_client_onecall.py`: Legacy OpenWeatherMap OneCall client (unused)

- **src/utils/**: Shared utilities
  - `image_processor.py`: Image optimization for e-ink
  - `config_manager.py`: Configuration persistence

- **scripts/**: Utility and helper scripts
  - `setup/`: Configuration scripts (timezone, display type, weather config)
  - `utils/`: Utility scripts (clear display, check directories, etc.)
  - `photo/`: Photo processing scripts
  - `debug/`: Debugging scripts
  - `fix/`: Bug fix scripts

- **tests/**: All test files organized by purpose
  - `test_simulation.py`: Simulation mode tests (works on any system)
  - `test_*.py`: Unit and integration tests
  - `hardware/`: Hardware diagnostic scripts
  - `color/`: Color display specific tests

## Agent Guidelines

### Code Organization

**IMPORTANT**: Keep root directory clean! All Python scripts and utilities should be in `scripts/` or `src/` directories.

**Root Directory**:
- `run.py` - Main entry point
- `requirements.txt` - Python dependencies
- `config/` - Configuration files
- `static/` - Static assets
- `templates/` - Web templates
- `docs/` - Documentation
- `AGENTS.md` - This file (replaces CLAUDE.md)

**Scripts Directory Structure**:
```
scripts/
├── setup/         # Configuration and setup
├── utils/          # Utilities and helpers
├── photo/          # Photo processing
├── debug/          # Debugging tools
└── fix/            # Repair scripts
```

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
- Location is determined via stored coordinates, geocoding, or IP geolocation
- Falls back to McHenry, IL if detection fails
- API requires User-Agent header with contact info
- Returns temperature, conditions, and current date
- Only covers US locations

**Location Detection Strategy (v1.2.0+)**:
1. Stored coordinates (primary) - User-set latitude/longitude via map picker
2. Geocode city/state (secondary) - For legacy config migration
3. IP-based geolocation (tertiary) - Uses ip-api.com
4. Hardcoded fallback (quaternary) - McHenry, IL coordinates

**Location Detection Strategy (v1.1.x)**:
1. IP-based geolocation (primary) - Uses ip-api.com
2. Configuration-based (secondary) - Reads city/state from config
3. Hardcoded fallback (tertiary) - McHenry, IL coordinates

**API Requirements**:
- Rate limiting: 30-second minimum between requests
- User-Agent header required for weather.gov
- No authentication required

### E-Ink Display Simulator

For development without hardware, use the e-ink simulator:

```python
from src.display.eink_simulator import EInkSimulator

# Create simulator instance
display = EInkSimulator(display_type="7in5_V2", color_mode="grayscale")
display.init()

# Display images
display.display_image_buffer(image)

# Simulated output saved to simulation/ directory
```

**Simulator Features**:
- Saves display output to `simulation/` directory
- Supports all display types (7in5_V2, 7in3f, etc.)
- Mimics e-ink refresh delays
- Adds simulation info overlays
- Creates PNG files for easy viewing

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
│   ├── lgpio_reset_test.py           # GPIO reset test
│   └── pin_check.py                  # GPIO interface availability checker
└── color/                             # Color display specific tests
    ├── color_test.py                 # ACeP 7-color display test
    └── color_display_test.py         # 7.3 inch ACeP 7-color e-ink display test
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

#### Testing Without Hardware

1. Use e-ink simulator for display testing:
   ```python
   from src.display.eink_simulator import EInkSimulator
   display = EInkSimulator()
   display.init()
   display.display_image_buffer(test_image)
   ```
2. Check output in `simulation/` directory
3. View generated PNG files to verify layout
4. Test weather and status bar rendering

#### Updating Weather Integration

1. Modify `src/weather/weather_client.py`
2. Ensure location detection has proper fallbacks
3. Test with different locations
4. Verify API response format changes
5. Run `tests/test_weather_api.py` to verify changes

#### Moving or Organizing Scripts

1. All utility scripts must be in `scripts/` directory
2. Organization:
   - `scripts/setup/` - Setup/configuration scripts
   - `scripts/utils/` - Utility scripts
   - `scripts/photo/` - Photo processing
   - `scripts/debug/` - Debugging
   - `scripts/fix/` - Repairs
3. Update documentation that references script paths
4. Update this AGENTS.md file
5. Verify imports and references are updated

### Branch Naming Convention

- `feature/` - New features
- `bugfix/` - Bug fixes
- `hotfix/` - Critical fixes for production
- `refactor/` - Code refactoring
- `chore/` - Maintenance tasks (no code changes)

### Commit Message Format

Follow conventional commits:
- `feat:` - New feature
- `fix:` - Bug fix
- `docs:` - Documentation changes
- `refactor:` - Code refactoring
- `test:` - Test changes
- `chore:` - Maintenance tasks
- `chore:organize:` - File organization
- `test:organize:` - Test file reorganization

## Version Management

### Semantic Versioning Format

Version format: **MAJOR.MINOR.PATCH** (e.g., 1.1.0)

- **MAJOR** (X.0.0): Breaking changes, API changes, architectural overhauls
  - Example: 1.5.2 → 2.0.0
- **MINOR** (0.X.0): New features, significant enhancements (backwards compatible)
  - Example: 1.5.2 → 1.6.0
- **PATCH** (0.0.X): Bug fixes, minor tweaks, performance improvements (backwards compatible)
  - Example: 1.5.2 → 1.5.3

### Decision Tree for Version Bumping

**MAJOR bump (X.0.0)** - Use when:
- Removing or renaming public components or APIs
- Changing component props in breaking ways
- Restructuring application architecture
- Database schema changes requiring migration
- Any change that requires users/developers to modify their code

**MINOR bump (0.X.0)** - Use when:
- Adding new feature or component
- Adding new props or options (backwards compatible)
- Significant enhancement to existing feature
- New API endpoints or services
- New user-facing functionality

**PATCH bump (0.0.X)** - Use when:
- Fixing bugs or errors
- Correcting typos in UI text
- Improving error messages or logging
- CSS/styling fixes or adjustments
- Performance optimizations (no API changes)
- Accessibility improvements
- Security patches

**SKIP version bump** - Use when:
- Updating documentation only (README, comments)
- Modifying AGENTS.md or workflow files
- File organization (chore:organize)
- CI/CD configurations
- .gitignore or similar tooling files

### AI Agent Workflow for Version Bumping

**Step 1: Analyze Changes**
Before creating a PR, review all changes in the branch and categorize them.

**Step 2: Ask User for Confirmation**
Present your analysis to the user and ask for confirmation:
```
Based on the changes in this branch, I've identified:
- [List key changes]

I recommend a [PATCH/MINOR/MAJOR] version bump because [reasoning].

Current version: X.Y.Z
Proposed version: X.Y.Z

Does this classification seem correct? Should I proceed with this version bump?
```

**Step 3: Apply Version Bump**
After user confirmation:
1. Update `src/version.py` with new version
2. Update AGENTS.md version history section
3. Commit with message: `chore: bump version to X.Y.Z`

**Step 4: Document in PR**
- Update PR title to include new version
- Mention version bump and reasoning in PR description
- List what changed to justify the bump type

### Version Bump Examples

**PATCH: 1.1.0 → 1.1.1**
- "Fix missing ImageFont import in simulator"
- "Correct weather data format mismatch"
- "Remove dead code references"

**MINOR: 1.1.1 → 1.2.0**
- "Add new /api/status endpoint"
- "Add color display support"
- "Implement photo upload preprocessing"

**MAJOR: 1.2.0 → 2.0.0**
- "Migrate from OpenWeatherMap to weather.gov API" (breaking config changes)
- "Redesign display driver architecture"
- "Change configuration file format"

### Integration with Workflow

Version bumping happens IN the feature branch, BEFORE creating the PR:

1. Create feature branch: `git checkout -b feature/description`
2. Make changes and test thoroughly
3. **Analyze changes and ask user about version bump type**
4. **Apply version bump** (update version.py and AGENTS.md)
5. Push branch: `git push`
6. Create PR with version noted in title/description
7. User reviews and merges to main

### Verification Commands

```bash
# Check current version
cat src/version.py | grep __version__

# View recent version bumps in git log
git log --oneline --grep="version" -10
```

### Human Override

Users can always override AI agent version decisions:
- Manually edit `src/version.py`
- Document reasoning in PR comments
- AI agents should defer to user judgment when corrected

### Code Review Checklist

Before submitting changes:
- [ ] Code follows project structure
- [ ] Root directory remains clean (scripts in `scripts/`, tests in `tests/`)
- [ ] No resource leaks (file handles, threads, etc.)
- [ ] Error handling is comprehensive
- [ ] Logging is appropriate
- [ ] Version has been updated if needed
- [ ] AGENTS.md has been updated
- [ ] Tests are in correct subdirectory
- [ ] Documentation references updated for paths
- [ ] Changes tested in simulation mode
- [ ] Documentation updated

## Project Structure

```
inkframe/
├── src/
│   ├── display/
│   │   ├── eink_driver.py
│   │   ├── eink_simulator.py
│   │   └── photo_manager.py
│   ├── web/
│   │   └── app.py
│   ├── weather/
│   │   ├── __init__.py
│   │   ├── weather_client.py
│   │   ├── weather_client_free.py
│   │   └── weather_client_onecall.py
│   ├── utils/
│   │   ├── config_manager.py
│   │   └── image_processor.py
│   ├── version.py
│   ├── __init__.py
│   └── main.py
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
│   │   ├── lgpio_reset_test.py
│   │   └── pin_check.py
│   └── color/
│       ├── color_test.py
│       └── color_display_test.py
├── scripts/
│   ├── setup/
│   │   ├── set_timezone.py
│   │   ├── set_display_type.py
│   │   └── set_weather_config.py
│   ├── utils/
│   │   ├── clear_display.py
│   │   ├── check_photos_dir.py
│   │   ├── check_uploads_dir.py
│   │   ├── check_processed_image.py
│   │   └── clear_weather_cache.py
│   ├── photo/
│   │   ├── preprocess_photos.py
│   │   ├── reprocess_one_photo.py
│   │   └── process_uploads_to_color.py
│   ├── debug/
│   │   ├── debug_display.py
│   │   ├── debug_photo_manager.py
│   │   ├── debug_waveshare.py
│   │   └── debug_color_issue.py
│   └── fix/
│       ├── fix_color_photos.py
│       └── check_bmp_colors.py
├── static/
│   ├── css/
│   ├── js/
│   ├── templates/
│   │   └── index.html
│   └── images/
│       └── photos/
├── config/
│   └── default_config.json
├── docs/
│   └── (documentation)
├── simulation/           # E-ink simulator output
├── run.py              # Main entry point
├── requirements.txt     # Dependencies
├── AGENTS.md          # This file (replaces CLAUDE.md)
├── README.md           # Project README
├── changelog.md       # Version history
└── troubleshooting.md   # Hardware troubleshooting guide
```

## API Reference

### Application Status

GET `/api/status`

Returns high-level application status including version:
```json
{
  "display": {
    "photo_count": 10,
    "display_type": "7in5_V2",
    "color_mode": "grayscale",
    "rotation_interval": 60
  },
  "weather": {
    "available": true,
    "temperature": "72°F",
    "condition": "Partly Cloudy",
    "date": "January 7, 2026"
  },
  "version": "1.1.1",
  "timestamp": "2026-01-07T14:30:00"
}
```

### System Status

GET `/api/system/status`

Returns detailed system information (disk, CPU, uptime):
```json
{
  "status": {
    "disk": {
      "total": "32.00 GB",
      "used": "4.50 GB",
      "free": "27.50 GB",
      "percent_used": 14.1
    },
    "uptime": 86400,
    "cpu_temp": "45.2°C",
    "display_running": true,
    "photo_count": 10,
    "timestamp": "2026-01-07T14:30:00"
  }
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

# Check available GPIO interfaces
python tests/hardware/pin_check.py

# Run full simulation test
python tests/test_simulation.py

# Test color display
python tests/color/color_test.py
```

See `tests/README.md` for comprehensive testing documentation.

## Utility Scripts

### Setup Scripts

```bash
# Set timezone
python scripts/setup/set_timezone.py

# Set display type
python scripts/setup/set_display_type.py

# Configure weather
python scripts/setup/set_weather_config.py
```

### Utility Scripts

```bash
# Clear display
python scripts/utils/clear_display.py

# Clear weather cache
python scripts/utils/clear_weather_cache.py

# Check photos directory
python scripts/utils/check_photos_dir.py

# Check uploads directory
python scripts/utils/check_uploads_dir.py

# Check processed images
python scripts/utils/check_processed_image.py
```

### Photo Processing

```bash
# Preprocess all photos
python scripts/photo/preprocess_photos.py

# Reprocess single photo
python scripts/photo/reprocess_one_photo.py

# Process uploads to color
python scripts/photo/process_uploads_to_color.py
```

### Debugging

```bash
# Debug display
python scripts/debug/debug_display.py

# Debug photo manager
python scripts/debug/debug_photo_manager.py

# Debug Waveshare driver
python scripts/debug/debug_waveshare.py

# Debug color issues
python scripts/debug/debug_color_issue.py
```

### Repairs

```bash
# Fix color photos
python scripts/fix/fix_color_photos.py

# Check BMP colors
python scripts/fix/check_bmp_colors.py
```

## Running the Application

### Development Mode (Simulation)

```bash
# Run with e-ink simulator
python -m src.display.eink_simulator

# Or import in code
from src.display.eink_simulator import EInkSimulator
display = EInkSimulator()
display.init()
```

### Production Mode (Hardware)

```bash
# Run full application
python run.py

# Run only web interface
python run.py --web-only

# Run only display component
python run.py --display-only

# Run with debug mode
python run.py --debug
```

## Weather Service Details

### Weather.gov API Integration

**Location Detection**:
1. IP-based geolocation via ip-api.com (free, no auth)
2. Configuration-based (city/state from config file)
3. Fallback to McHenry, IL (42.3333° N, 88.6167° W)

**API Endpoints Used**:
- `GET /points/{lat},{lon}` - Get NWS grid information
- `GET /gridpoints/{wfo},{x},{y}/forecast` - Get daily forecast
- `GET /stations/{stationId}/observations/latest` - Get current conditions

**Rate Limiting**:
- 30-second minimum between API requests (NWS requirement)
- Request caching to reduce API calls
- Queue for rate-limited requests with retries

**Data Format**:
```python
{
    "current": {
        "temp": 72,                    # Fahrenheit
        "condition": "Partly Cloudy",
        "description": "Partly Cloudy",
        "humidity": 65,
        "wind_speed": 8,
        "feels_like": "N/A",
        "icon": "https://api.weather.gov/icons/..."
    },
    "date": "June 15, 2025",
    "has_alert": False,
    "raw_data": {...}
}
```

**Limitations**:
- US locations only (weather.gov limitation)
- No "feels like" temperature from NWS
- 30-second rate limit enforced
- Requires User-Agent header

## Display Simulator

### Purpose

The e-ink display simulator allows testing and development without physical hardware by:
- Saving display output to image files
- Simulating refresh delays
- Supporting all display types
- Adding simulation metadata overlays

### Usage

```python
from src.display.eink_simulator import EInkSimulator

# Create simulator for specific display type
display = EInkSimulator(display_type="7in5_V2", color_mode="grayscale")

# Initialize
display.init()

# Display images
display.display_image_buffer(image, force_refresh=True)

# Clear
display.clear()

# Sleep mode
display.sleep()

# Get display info
info = display.get_display_info()
```

### Output

Simulated displays are saved as PNG files in the `simulation/` directory:
- `<display_type>_display_<timestamp>.png` - Normal display
- `<display_type>_clear_<timestamp>.png` - Cleared display
- `<display_type>_sleep_<timestamp>.png` - Sleep mode

Each output includes:
- Timestamp of operation
- Display type and mode
- Refresh count
- Operation type (display, clear, sleep)

## Troubleshooting

### Common Issues

1. **Display Not Initializing**
   - Check GPIO/SPI with `tests/hardware/simple_test.py`
   - Verify display model with `tests/hardware/check_model.py`
   - Check physical connections

2. **Weather Not Showing**
   - Check logs for API errors
   - Verify internet connection
   - Check if outside US (weather.gov limitation)

3. **Photos Not Displaying**
   - Check photo directory configuration
   - Verify photos are in correct format (BMP preferred)
   - Check file permissions

4. **Service Status Issues**
   - Both `running` and `started` flags should be checked
   - `running` = actively cycling
   - `started` = initialized (may not be cycling)

### Logs

```bash
# View application logs
tail -f inkframe.log

# Filter for specific components
grep "weather" inkframe.log
grep "display" inkframe.log
grep "error" inkframe.log
```

## Testing Without Hardware

When developing on a system without the e-ink display:

1. **Use Simulator**: All display operations can be simulated
   ```python
   from src.display.eink_simulator import EInkSimulator
   display = EInkSimulator()
   display.init()
   display.display_image_buffer(test_image)
   ```

2. **Check Output**: Review generated PNG files in `simulation/` directory

3. **Test Web Interface**:
   ```bash
   python run.py --web-only
   # Navigate to http://localhost:5000
   ```

4. **Run Unit Tests**:
   ```bash
   python tests/test_simulation.py
   python tests/test_display.py
   python tests/test_weather_api.py
   ```

## Version Management

### Semantic Versioning

Version format: **MAJOR.MINOR.PATCH** (e.g., 1.1.0)

- **MAJOR** (X.0.0): Breaking changes, API changes, architectural overhauls
  - Example: 1.5.2 → 2.0.0
- **MINOR** (0.X.0): New features, significant enhancements (backwards compatible)
  - Example: 1.5.2 → 1.6.0
- **PATCH** (0.0.X): Bug fixes, minor tweaks, performance improvements (backwards compatible)
  - Example: 1.5.2 → 1.5.3

### Version Bump Workflow

1. **Analyze Changes**: Review all changes in the branch
2. **Categorize**: Determine if MAJOR, MINOR, or PATCH
3. **Ask User**: Present analysis and get confirmation
4. **Update Version**: Modify `src/version.py`
5. **Update AGENTS.md**: Add version history entry
6. **Commit**: Version bump commit

### Decision Tree

**MAJOR bump** - Use when:
- Removing or renaming public components or APIs
- Changing component props in breaking ways
- Restructuring application architecture
- Database schema changes requiring migration

**MINOR bump** - Use when:
- Adding new feature or component
- Adding new props or options (backwards compatible)
- Significant enhancement to existing feature
- New API endpoints or services
- New user-facing functionality

**PATCH bump** - Use when:
- Fixing bugs or errors
- Correcting typos in UI text
- Improving error messages or logging
- CSS/styling fixes or adjustments
- Performance optimizations (no API changes)

**SKIP version bump** - Use when:
- Updating documentation only
- Modifying AGENTS.md or workflow files
- File organization (chore:organize)
- CI/CD configurations
- .gitignore or similar tooling files

## Known Limitations

### Weather Service

- US locations only (weather.gov provides US data only)
- 30-second rate limit on API requests
- No "feels like" temperature available
- Some areas may lack nearby observation stations

### Display Hardware

- E-ink refresh takes 35+ seconds for full update
- Limited grayscale/color capabilities
- Partial refresh may cause ghosting artifacts
- Power requirements during initialization

### Location Detection

- IP geolocation relies on external service availability
- Fallback always to McHenry, IL if all detection fails
- Location data cached in memory for session

## Security Considerations

- No sensitive data in weather.gov (public API)
- User-Agent required by NWS for identification
- API key not required (security benefit)
- Location detection uses IP geolocation (privacy consideration)

## Performance Optimization

- Weather data cached for 30 minutes (configurable)
- Display refresh minimized to conserve power
- Images processed at upload time, not display time
- BMP format preferred for faster e-ink rendering
- Rate limiting on weather API to avoid bans

## Maintenance Tasks

Regular maintenance recommended:
- Clear weather cache monthly: `python scripts/utils/clear_weather_cache.py`
- Preprocess new photos: `python scripts/photo/preprocess_photos.py`
- Check display hardware: `python tests/hardware/check_model.py`
- Review logs for errors: `grep "error" inkframe.log`

## Contact and Support

For issues or questions:
1. Check `troubleshooting.md` for common solutions
2. Review logs for error messages
3. Run hardware tests to verify functionality
4. Test with e-ink simulator to reproduce issues
5. Check GitHub issues for known problems