# Changelog

All notable changes to the InkFrame project will be documented in this file.

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