# Changelog

All notable changes to the InkFrame project will be documented in this file.

## [1.1.0] - 2025-06-15

### Added
- Migrated from OpenWeatherMap to weather.gov API for weather data
- IP-based geolocation to automatically determine weather location
- Current date display in status bar (Month Day, Year format)
- Version number display in ghost text on bottom left of screen
- AGENTS.md file for AI agent guidance
- Tests/README.md with comprehensive testing documentation
- Version management system with src/version.py

### Changed
- Reorganized all test files into tests/ directory structure
- Moved hardware diagnostic scripts to tests/hardware/
- Moved color display tests to tests/color/
- Updated all documentation references to new test file paths
- Enhanced display service status reporting with 'started' flag

### Fixed
- Display service reporting as "not started" when it was actually running
- Weather client location detection now has proper fallback mechanism
- Test file organization - all tests now properly categorized

### Dependencies
- Removed OpenWeatherMap API dependency
- No new dependencies required

## [0.1.2] - 2025-05-23

### Added
- Support for 7.3 inch color e-ink display (7in3f ACeP 7-color)
- Center cropping feature for photos to fill the entire screen without side bars
- Timezone configuration script (set_timezone.py) with automatic detection
- Placeholder for partial refresh clock updates (implementation pending)
- Comments about e-ink clock update limitations
- Test script for ACeP photo processing (test_acep_photos.py)

### Fixed
- Fixed color inversion issue on 7-color displays by removing palette quantization
- Fixed incorrect background color handling for RGB mode displays
- Fixed side bar color issues when displaying photos on color displays
- Fixed color image processing to properly quantize to 7 ACeP colors with dithering
- Fixed display not clearing on service startup/shutdown
- Fixed weather client returning wrong data format causing N/A display
- Fixed display clear to reinitialize if needed
- Fixed systemd service file to run correct entry point (run.py instead of photo_manager.py)
- Fixed inverted colors by adding ImageOps.invert for 7in3f driver
- Fixed timezone list to use proper America/Chicago format

### Changed
- Images for color displays now properly quantize to the 7 available ACeP colors
- Photo display now uses center cropping instead of letterboxing to avoid side bars
- Added proper color mapping for ACeP display (Black, White, Red, Green, Blue, Yellow, Orange)
- Web upload now automatically processes images to color when color mode is configured

### Removed
- Clock mode removed (not suitable for e-ink displays with 35-second refresh)
- Time display removed from status bar (only weather shown now)

## [0.1.1] - 2025-05-19

### Added
- Enhanced E-Ink display driver with advanced features
  - Support for grayscale display (4-level)
  - Intelligent refresh patterns to reduce ghosting
  - Display diagnostic capabilities
  - Multiple refresh modes (full and partial)
- Advanced image processing utilities
  - Multiple dithering algorithms
  - Enhanced contrast and brightness adjustments
  - Specialty image filters for e-ink optimization
  - Support for HEIC image format
- Photo management system
  - Intelligent photo selection with weighted algorithm
  - Multiple display modes (photos, clock, information)
  - Historical tracking of viewed photos
  - Support for external control via signals
- Comprehensive OpenWeatherMap client
  - Forecast data for upcoming days
  - Weather alerts and warnings
  - Intelligent caching to reduce API calls
  - Detailed weather information display
  - Sunrise/sunset information

### Changed
- Updated todo.md to reflect completed core components
- Enhanced documentation with implementation details

### Fixed
- Improved error handling throughout the application
- Fixed potential memory issues in image processing

## [0.1.0] - 2025-05-19

### Added
- Initial project structure setup
- Created README.md with project overview, features, and architecture diagram
- Added documentation files (installation guide, user manual, API docs, development guide)
- Setup basic application files structure in src/ directory
- Created CLAUDE.md file for Claude Code to understand the project
- Added installation script (install.sh)
- Created simulation test for non-Raspberry Pi development
- Set up requirements.txt with dependencies
- Implemented configuration management system with JSON storage
- Added default configuration with display, photos, weather, and system settings
- Implemented systemd service files for web and display components
- Set up logging system with file and console handlers

### Changed
- Updated todo.md to reflect completed setup tasks

### Fixed
- N/A