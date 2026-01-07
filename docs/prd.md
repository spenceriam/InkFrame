# InkFrame - E-Ink Digital Photo Frame

## Product Requirements Document

### Overview
InkFrame is a minimalist digital photo frame solution that runs on a Raspberry Pi Zero W connected to a Waveshare 7.5" e-ink display. The system automatically displays photos with an information bar showing time and weather, and offers a simple web interface for management.

### Hardware Requirements
- Raspberry Pi Zero W
- Waveshare 7.5" e-ink display with HAT
- microSD card (min 8GB recommended)
- Power supply for Raspberry Pi

### Functional Requirements

#### Display System
- **Auto-start**: System launches automatically on Pi boot
- **Photo Display**: Full-screen photos optimized for e-ink display
- **Image Rotation**: Automatically cycle through photos at configurable intervals
- **Status Bar**: Show current time and local weather at bottom of display
- **Graceful Error Handling**: Display fallback image if problems occur

#### Web Administration Interface
- **Photo Management**:
  - Upload new photos (JPG, PNG, HEIC support)
  - Delete existing photos
  - View all available photos
- **Configuration**:
  - Set photo rotation interval (default: 1 hour)
  - Configure timezone settings
  - Set location for weather (city, state, country)
  - Input OpenWeatherMap API key
- **System Management**:
  - View system status (disk space, uptime)
  - Access terminal (optional, advanced users)
  - Update application

#### Weather Integration
- Display current temperature and conditions
- Use OpenWeatherMap API (free tier)
- Cache weather data to minimize API calls
- Show timestamp of last weather update

### Non-Functional Requirements

#### Performance
- Optimize for Pi Zero W resource constraints (1GHz CPU, 512MB RAM)
- Efficient image processing to limit CPU usage
- Pre-process images upon upload to avoid runtime processing
- Limit memory usage during image display cycles

#### Usability
- Intuitive web interface accessible from mobile devices
- Clear error messages for troubleshooting
- Documentation for setup and operation

#### Reliability
- Graceful error handling for network/API issues
- Recovery mechanisms for power loss
- Logging for diagnostic purposes

### Technical Requirements

#### Software Components
- **Display Application**: Python-based using Waveshare e-paper library and Pillow
- **Web Backend**: Flask application providing REST API and web interface
- **Image Processing**: Pillow for conversions with optional ImageMagick for HEIC
- **Configuration**: JSON-based configuration storage
- **Weather Integration**: OpenWeatherMap API client with caching
- **System Integration**: Systemd services for auto-start

#### Storage
- Photos stored in local filesystem
- Configuration in JSON file
- Weather cache in temporary storage

#### Networking
- Wi-Fi connectivity via Pi Zero W
- Local web server for administration
- External API calls for weather data

### Future Enhancements (Not in Initial Scope)
- External storage support (USB drive)
- Remote photo synchronization (cloud services)
- Advanced display transitions
- Multiple user accounts
- Screen sleep/wake scheduling