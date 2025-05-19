# InkFrame User Manual

Welcome to InkFrame, your minimal, elegant digital photo frame solution for Raspberry Pi with e-ink display.

## Accessing the Web Interface

You can access the InkFrame web interface using any web browser on a device connected to the same network as your Raspberry Pi:

1. Open a web browser (Chrome, Firefox, Safari, etc.)
2. Enter the address: `http://inkframe.local` or `http://[your-pi-ip-address]`
3. The InkFrame web interface should load, showing the Photos tab

## Interface Overview

The web interface is divided into three main tabs:

1. **Photos**: Upload, view, and manage your photos
2. **Settings**: Configure display, weather, and system settings
3. **System**: View system information, logs, and control the display service

## Managing Photos

### Uploading Photos

1. Navigate to the **Photos** tab
2. Drag and drop photos onto the upload area, or click to select files
3. Supported formats: JPG, PNG, BMP, HEIC/HEIF
4. Photos will be automatically processed and optimized for the e-ink display
5. Progress will be shown during upload

### Viewing Photos

The photo gallery shows all uploaded photos with thumbnails. For each photo, you can see:
- A preview thumbnail
- The filename
- The date added

### Deleting Photos

1. Find the photo you want to delete in the gallery
2. Click the "Delete" button below the photo
3. Confirm the deletion when prompted

### Refreshing the Display

To manually change the photo on the e-ink display:
1. Click the "Refresh Display" button at the top of the Photos tab
2. The system will select a random photo and display it on the e-ink screen

## Configuring Settings

### Display Settings

Under the **Settings** tab:

1. **Photo Rotation Interval**: Set how often (in minutes) the photo should change
   - Default: 60 minutes
   - Range: 1-1440 minutes (24 hours)

2. **Enable Image Dithering**: Toggle dithering for better grayscale appearance
   - Recommended: Enabled
   - When enabled, photos will have better gray tone representation
   - When disabled, photos will have higher contrast

### Weather Settings

To display weather information on the status bar:

1. **City**: Enter your city name (required)
2. **State/Province**: Enter your state or province (optional)
3. **Country Code**: Enter your country code (e.g., US, UK, CA)
4. **Temperature Units**: Choose between Celsius (metric) or Fahrenheit (imperial)
5. **OpenWeatherMap API Key**: Enter your API key
   - Get a free API key at [openweathermap.org](https://openweathermap.org/api)
   - Sign up for a free account and copy your API key

After entering your weather settings:
1. Click "Test Weather Data" to verify your settings
2. If successful, you'll see the current weather for your location
3. If there's an error, check your settings and API key

### System Settings

1. **Timezone**: Select your timezone for accurate time display

### Saving Settings

After making changes to any settings:
1. Click the "Save Settings" button at the top of the page
2. Your settings will be applied immediately

## System Information

The **System** tab provides information about the InkFrame system:

### Storage Information

Shows disk usage information:
- Total disk space
- Used disk space
- Free disk space
- Percentage used

### Display Service

Shows the status of the photo display service:
- **Running**: The service is active and cycling photos
- **Stopped**: The service is not running

If the service is stopped, click "Start Service" to restart it.

### System Details

Displays general system information:
- Uptime (how long the system has been running)
- CPU temperature
- Number of photos in the library
- Last update timestamp

### System Logs

Shows the most recent system logs, useful for troubleshooting.
Click "Refresh Status" to update the system information and logs.

## Frequently Asked Questions

### How often does the weather information update?

Weather data is updated every 30 minutes by default. The weather shown on the display refreshes when the photo changes.

### Why does the e-ink display take time to refresh?

E-ink displays have a relatively slow refresh rate compared to LCD screens. This is normal for e-ink technology and helps maintain the low power consumption that makes e-ink ideal for this application.

### How many photos can I store?

The number of photos depends on your SD card size. As a rough guideline:
- 8GB SD card: approximately 1000-2000 photos (after OS and application)
- 16GB or larger: several thousand photos

### My photos look different on the e-ink display than on my computer

E-ink displays have limited grayscale capabilities, typically showing just 16 shades of gray. InkFrame processes your photos to look their best on this type of display, but they will appear different from color displays.

### How do I update InkFrame?

See the [Installation Guide](installation.md) for update instructions.

## Troubleshooting

### The web interface isn't loading

1. Check that your Raspberry Pi is powered on and connected to your network
2. Try accessing by IP address instead of hostname
3. Restart the web service: `sudo systemctl restart inkframe-web.service`

### Photos aren't changing on the display

1. Check if the display service is running in the System tab
2. If not, click "Start Service"
3. You can also check from the command line: `sudo systemctl status inkframe-display.service`

### Weather information isn't showing

1. Verify your API key and location settings are correct
2. Use the "Test Weather Data" button to validate your settings
3. Check system logs for any API errors

### The e-ink display is blank or showing an error

1. Verify that the HAT is properly connected to the Raspberry Pi
2. Restart the display service: `sudo systemctl restart inkframe-display.service`
3. Check system logs for hardware errors

If problems persist, check the logs in the System tab or via SSH:
```
sudo journalctl -u inkframe-web.service
sudo journalctl -u inkframe-display.service
```