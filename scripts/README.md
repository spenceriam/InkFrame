# Scripts Directory

This directory contains utility, setup, debugging, and maintenance scripts for InkFrame.

## Directory Structure

```
scripts/
├── setup/              # Configuration and setup scripts
├── utils/               # Utility and helper scripts
├── photo/              # Photo processing scripts
├── debug/              # Debugging and troubleshooting scripts
└── fix/                # Bug fix and repair scripts
```

## Setup Scripts (`setup/`)

Scripts for configuring and setting up InkFrame.

### set_timezone.py

Sets the system timezone for InkFrame.

**Usage:**
```bash
python scripts/setup/set_timezone.py
```

**What it does:**
- Detects timezone from IP geolocation
- Updates system timezone configuration
- Prompts for manual timezone selection if auto-detection fails

**When to use:**
- Initial system setup
- After moving to a different time zone
- When timezone is incorrect

---

### set_display_type.py

Configures the e-ink display type and color mode.

**Usage:**
```bash
python scripts/setup/set_display_type.py
```

**What it does:**
- Lists available display types (7in5_V2, 7in3f, etc.)
- Prompts for display selection
- Configures color mode (grayscale, color, bw)
- Updates configuration file

**When to use:**
- Initial hardware setup
- After changing display hardware
- When switching between color and grayscale modes

---

### set_weather_config.py

Configures weather service settings.

**Usage:**
```bash
python scripts/setup/set_weather_config.py
```

**What it does:**
- Prompts for weather service configuration
- Sets city/state (optional, for geocoding)
- Configures update interval
- Sets units preference

**When to use:**
- Initial setup
- When changing preferred location
- Adjusting weather update frequency

---

## Utility Scripts (`utils/`)

General utility and helper scripts.

### clear_display.py

Manually clears the e-ink display.

**Usage:**
```bash
python scripts/utils/clear_display.py
```

**What it does:**
- Clears the display using direct driver access
- Useful for troubleshooting
- Forces a clean slate

**When to use:**
- Troubleshooting display issues
- Preparing display for new content
- Testing display functionality

---

### clear_weather_cache.py

Clears the weather data cache.

**Usage:**
```bash
python scripts/utils/clear_weather_cache.py
```

**What it does:**
- Removes cached weather data
- Forces fresh weather fetch on next update
- Useful for troubleshooting weather issues

**When to use:**
- Weather not updating correctly
- After changing location
- Troubleshooting weather API issues

---

### check_photos_dir.py

Verifies the photos directory structure and contents.

**Usage:**
```bash
python scripts/utils/check_photos_dir.py
```

**What it does:**
- Checks if photos directory exists
- Lists photo files found
- Verifies file permissions
- Reports statistics

**When to use:**
- Troubleshooting photo display issues
- Verifying upload functionality
- Checking file organization

---

### check_uploads_dir.py

Verifies the uploads directory.

**Usage:**
```bash
python scripts/utils/check_uploads_dir.py
```

**What it does:**
- Checks if uploads directory exists
- Lists uploaded files
- Verifies file permissions
- Reports upload statistics

**When to use:**
- Troubleshooting upload issues
- Verifying web interface functionality
- Checking file organization

---

### check_processed_image.py

Verifies a processed image file.

**Usage:**
```bash
python scripts/utils/check_processed_image.py <image_path>
```

**What it does:**
- Verifies image was processed correctly
- Checks dimensions and format
- Verifies file integrity

**When to use:**
- Troubleshooting processed photos
- Verifying image processing pipeline
- Checking specific photo issues

---

## Photo Processing Scripts (`photo/`)

Scripts for processing and managing photos.

### preprocess_photos.py

Preprocesses all photos in the photos directory for e-ink display.

**Usage:**
```bash
python scripts/photo/preprocess_photos.py
```

**What it does:**
- Processes all photos to BMP format
- Optimizes for e-ink display
- Applies dithering if configured
- Creates color versions for color displays
- Resizes to display dimensions

**When to use:**
- Initial setup after uploading photos
- After changing display type or settings
- When updating image processing parameters

**Parameters:**
- Display type (from config)
- Color mode (from config)
- Dithering setting (from config)
- Target dimensions (from config)

---

### reprocess_one_photo.py

Reprocesses a single photo.

**Usage:**
```bash
python scripts/photo/reprocess_one_photo.py <photo_path>
```

**What it does:**
- Processes single photo to correct format
- Applies current display settings
- Optimizes for e-ink display
- Overwrites existing processed version

**When to use:**
- Single photo has issues
- After changing processing settings
- Testing new processing parameters

---

### process_uploads_to_color.py

Processes uploaded photos to color format for ACeP displays.

**Usage:**
```bash
python scripts/photo/process_uploads_to_color.py
```

**What it does:**
- Converts uploaded photos to 7-color ACeP format
- Applies color quantization
- Creates optimized BMP files
- Preserves original files

**When to use:**
- Switching to color display mode
- After uploading new photos
- When color photos display incorrectly

**Color Mapping:**
- Uses ACeP 7-color palette:
  - Black, White, Red, Green, Blue, Yellow, Orange

---

## Debugging Scripts (`debug/`)

Scripts for debugging and troubleshooting InkFrame.

### debug_display.py

Debugs e-ink display functionality.

**Usage:**
```bash
python scripts/debug/debug_display.py
```

**What it does:**
- Tests display initialization
- Displays test patterns
- Logs detailed diagnostic information
- Tests refresh capabilities

**When to use:**
- Display not working
- Testing new display hardware
- Verifying display driver

---

### debug_photo_manager.py

Debugs photo manager functionality.

**Usage:**
```bash
python scripts/debug/debug_photo_manager.py
```

**What it does:**
- Tests photo selection logic
- Displays rotation timing
- Tests weighted selection algorithm
- Logs photo cycle information

**When to use:**
- Photos not cycling correctly
- Testing new rotation settings
- Verifying photo selection logic

---

### debug_waveshare.py

Debugs Waveshare e-ink driver.

**Usage:**
```bash
python scripts/debug/debug_waveshare.py
```

**What it does:**
- Tests driver import
- Verifies hardware communication
- Tests GPIO and SPI connections
- Logs driver capabilities

**When to use:**
- Hardware not detected
- Testing Waveshare library
- GPIO/SPI communication issues

---

### debug_color_issue.py

Debugs color display issues.

**Usage:**
```bash
python scripts/debug/debug_color_issue.py
```

**What it does:**
- Tests color conversion
- Displays color test patterns
- Verifies ACeP 7-color support
- Logs color processing details

**When to use:**
- Colors not displaying correctly
- Testing ACeP color display
- After color processing changes

---

## Fix/Repair Scripts (`fix/`)

Scripts for fixing and repairing issues.

### fix_color_photos.py

Repairs color photo processing issues.

**Usage:**
```bash
python scripts/fix/fix_color_photos.py [options]
```

**Options:**
- `--all` - Reprocess all color photos
- `--file <path>` - Repair specific file
- `--dry-run` - Show what would be done without changes

**What it does:**
- Reprocesses photos with corrected color mapping
- Applies latest processing parameters
- Fixes palette quantization issues
- Preserves original files

**When to use:**
- Color photos have wrong colors
- After updating color processing
- Fixing palette issues

---

### check_bmp_colors.py

Checks BMP file color values.

**Usage:**
```bash
python scripts/fix/check_bmp_colors.py <bmp_file>
```

**What it does:**
- Analyzes BMP file color values
- Verifies correct palette usage
- Reports color distribution
- Identifies potential issues

**When to use:**
- Verifying BMP color correctness
- Troubleshooting color display issues
- Checking processed photo quality

---

## Running Scripts

### From Project Root

Most scripts should be run from the project root directory:

```bash
cd /path/to/inkframe
python scripts/setup/set_timezone.py
python scripts/utils/check_photos_dir.py
# etc.
```

### Making Scripts Executable

To run scripts without `python` prefix:

```bash
chmod +x scripts/setup/*.py
chmod +x scripts/utils/*.py
# Then run directly:
./scripts/setup/set_timezone.py
```

---

## Common Use Cases

### Initial Setup

```bash
# 1. Set up timezone
python scripts/setup/set_timezone.py

# 2. Configure display type
python scripts/setup/set_display_type.py

# 3. Configure weather
python scripts/setup/set_weather_config.py

# 4. Preprocess photos
python scripts/photo/preprocess_photos.py
```

### Troubleshooting Display

```bash
# 1. Check display driver
python tests/hardware/simple_test.py

# 2. Debug display
python scripts/debug/debug_display.py

# 3. Clear display
python scripts/utils/clear_display.py

# 4. Check display model
python tests/hardware/check_model.py
```

### Troubleshooting Photos

```bash
# 1. Check photos directory
python scripts/utils/check_photos_dir.py

# 2. Reprocess problematic photo
python scripts/photo/reprocess_one_photo.py path/to/photo.jpg

# 3. Reprocess all photos
python scripts/photo/preprocess_photos.py
```

### Troubleshooting Weather

```bash
# 1. Clear weather cache
python scripts/utils/clear_weather_cache.py

# 2. Check weather config
cat config/default_config.json | grep -A 10 "weather"

# 3. Test weather API
python tests/test_weather_api.py
```

---

## Script Guidelines

### When Creating New Scripts

1. **Choose Correct Directory**:
   - `setup/` - Configuration and setup
   - `utils/` - General utilities
   - `photo/` - Photo-related
   - `debug/` - Troubleshooting
   - `fix/` - Repairs and fixes

2. **Include Documentation**:
   - Script description
   - Usage examples
   - What it does
   - When to use it

3. **Add Error Handling**:
   - Try/except blocks
   - User-friendly error messages
   - Logging for debugging

4. **Make Scripts Robust**:
   - Check for dependencies
   - Verify file existence
   - Handle configuration missing
   - Provide helpful output

5. **Update Documentation**:
   - Add to this README
   - Update AGENTS.md if relevant
   - Include in usage examples

---

## Dependencies

### System Dependencies

- Python 3.7+
- Pillow (PIL) for image processing
- pytz for timezone handling
- requests for API calls
- waveshare_epd (for display scripts)

### Configuration

Scripts read from:
- `config/default_config.json` - Default configuration
- `config/config.json` - User overrides

---

## Troubleshooting Scripts

### Script Won't Run

1. **Check Python Version**:
   ```bash
   python --version  # Should be 3.7+
   ```

2. **Check Dependencies**:
   ```bash
   pip list | grep -E "pillow|requests|pytz"
   ```

3. **Check Script Path**:
   - Must run from project root
   - Use `python scripts/...` syntax
   - Or make scripts executable

4. **Check Configuration**:
   ```bash
   cat config/default_config.json
   ```

### Script Hangs

1. **Check Hardware Connection**:
   - Display scripts require e-ink hardware
   - Try simulation mode instead

2. **Check for Lock Files**:
   - Remove any `.lock` files
   - Check for zombie processes

3. **Check Logs**:
   ```bash
   tail -f inkframe.log
   ```

---

## Integration with Main Application

### Automatic Script Execution

The main application (`run.py`) automatically handles:
- Display initialization
- Weather updates
- Photo processing on upload
- Configuration changes

No manual script execution required during normal operation.

### Manual Script Execution

Scripts are primarily for:
- Initial setup
- Troubleshooting
- Maintenance
- Testing

---

## Security Considerations

### File Permissions

Scripts run with same permissions as user:
- Use appropriate file permissions
- Sensitive operations may need sudo
- Avoid storing passwords in scripts

### Configuration

Configuration files should be:
- Readable by application user
- Not world-writable
- Backed up before modifications

---

## Performance Tips

### Photo Processing

- Process photos in batches
- Use BMP format for e-ink
- Preprocess when possible, not at display time
- Use appropriate dithering settings

### Maintenance

- Run maintenance scripts regularly
- Clear caches periodically
- Check disk space for photos
- Review logs for issues

---

## Script Development

### Best Practices

1. **Modular Design**: Each script does one thing well
2. **Error Handling**: Graceful failures with helpful messages
3. **Logging**: Use Python logging module
4. **Documentation**: Clear usage and description
5. **Testing**: Test with different scenarios

### Example Template

```python
#!/usr/bin/env python3
"""
Brief description of what this script does.
"""

import logging
import sys
from pathlib import Path

logger = logging.getLogger(__name__)

def main():
    """Main function"""
    logger.info("Script started")
    
    # Your script logic here
    
    logger.info("Script completed")

if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO)
    main()
```

---

## Related Documentation

- **AGENTS.md** - Overall development guidelines
- **tests/README.md** - Test documentation
- **troubleshooting.md** - Hardware troubleshooting
- **README.md** - Project overview

---

## Contributing

When adding new scripts:
1. Place in appropriate subdirectory
2. Add documentation to this README
3. Include usage examples
4. Test thoroughly
5. Update AGENTS.md if relevant
6. Commit with descriptive message

---

## Version History

### v1.1.0 - 2025-06-15

- Created scripts directory structure
- Organized all root-level utility scripts
- Created comprehensive documentation
- Added setup, utils, photo, debug, and fix subdirectories