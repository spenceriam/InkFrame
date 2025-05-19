# InkFrame API Documentation

InkFrame provides a RESTful API for programmatic control of the photo frame. This document details the available endpoints and their usage.

## Base URL

All API endpoints are accessible at:

```
http://[your-pi-ip]:5000/api
```

## Authentication

The API does not currently implement authentication. It is designed for use on a trusted local network.

## Photo Management

### List All Photos

**Endpoint**: `GET /api/photos`

**Description**: Returns a list of all photos in the library with their metadata.

**Response Example**:
```json
{
  "photos": [
    {
      "id": "sunset",
      "name": "sunset.jpg",
      "url": "/static/images/photos/sunset.jpg",
      "thumbnail": "/static/images/photos/thumbnails/sunset.jpg",
      "date_added": "2023-03-15T10:23:45"
    },
    {
      "id": "mountain",
      "name": "mountain.png",
      "url": "/static/images/photos/mountain.png",
      "thumbnail": "/static/images/photos/thumbnails/mountain.jpg",
      "date_added": "2023-03-14T15:42:22"
    }
  ]
}
```

### Upload Photo

**Endpoint**: `POST /api/photos`

**Description**: Uploads a new photo to the library.

**Request**: Multipart form data with a file field named "file".

**Response Example**:
```json
{
  "success": true,
  "message": "File uploaded and processed successfully",
  "filename": "landscape.jpg"
}
```

### Delete Photo

**Endpoint**: `DELETE /api/photos/<photo_id>`

**Description**: Deletes a photo from the library.

**Parameters**:
- `photo_id`: The ID of the photo to delete (usually the filename without extension)

**Response Example**:
```json
{
  "success": true,
  "message": "Photo deleted successfully"
}
```

### Refresh Display

**Endpoint**: `POST /api/refresh`

**Description**: Manually refreshes the e-ink display with a new randomly selected photo.

**Response Example**:
```json
{
  "success": true,
  "message": "Display refreshed with a new photo"
}
```

## Configuration Management

### Get Configuration

**Endpoint**: `GET /api/config`

**Description**: Retrieves the current configuration settings.

**Response Example**:
```json
{
  "config": {
    "display": {
      "rotation_interval_minutes": 60,
      "status_bar_height": 40,
      "enable_dithering": true
    },
    "photos": {
      "directory": "static/images/photos",
      "max_width": 800,
      "max_height": 440,
      "format": "bmp"
    },
    "weather": {
      "api_key": "abcd****",
      "city": "London",
      "state": "",
      "country": "UK",
      "units": "metric",
      "update_interval_minutes": 30,
      "cache_expiry_minutes": 120
    },
    "system": {
      "timezone": "Europe/London",
      "web_port": 5000,
      "debug_mode": false,
      "log_level": "INFO"
    }
  }
}
```

### Update Configuration

**Endpoint**: `POST /api/config`

**Description**: Updates the configuration settings.

**Request Body**: JSON object with configuration sections to update.

**Example Request**:
```json
{
  "display": {
    "rotation_interval_minutes": 30,
    "enable_dithering": false
  },
  "weather": {
    "city": "Paris",
    "country": "FR",
    "units": "metric"
  }
}
```

**Response Example**:
```json
{
  "success": true,
  "message": "Configuration updated successfully"
}
```

## Weather Information

### Get Weather

**Endpoint**: `GET /api/weather`

**Description**: Gets the current weather data.

**Response Example**:
```json
{
  "weather": {
    "temp": 15,
    "condition": "Clear",
    "description": "clear sky",
    "humidity": 65,
    "wind_speed": 3.5,
    "icon": "01d",
    "location": "London",
    "country": "GB"
  }
}
```

### Refresh Weather

**Endpoint**: `POST /api/weather/refresh`

**Description**: Forces a refresh of the weather data from the API.

**Response Example**:
```json
{
  "weather": {
    "temp": 15,
    "condition": "Clear",
    "description": "clear sky",
    "humidity": 65,
    "wind_speed": 3.5,
    "icon": "01d",
    "location": "London",
    "country": "GB"
  },
  "message": "Weather data refreshed"
}
```

## System Information

### Get System Status

**Endpoint**: `GET /api/system/status`

**Description**: Gets system status information.

**Response Example**:
```json
{
  "status": {
    "disk": {
      "total": "14.5 GB",
      "used": "3.2 GB",
      "free": "11.3 GB",
      "percent_used": 22.1
    },
    "uptime": 86420,
    "cpu_temp": "42.5°C",
    "display_running": true,
    "photo_count": 15,
    "timestamp": "2023-03-15T12:34:56"
  }
}
```

### Start Display Service

**Endpoint**: `POST /api/system/start`

**Description**: Starts the photo display service if it's not running.

**Response Example**:
```json
{
  "success": true,
  "message": "Display service started"
}
```

### Get System Logs

**Endpoint**: `GET /api/system/logs`

**Description**: Retrieves recent system logs.

**Query Parameters**:
- `lines` (optional): Number of lines to return (default: 100)

**Response Example**:
```json
{
  "logs": [
    "2023-03-15 12:34:56 - INFO - Starting photo display service",
    "2023-03-15 12:34:58 - INFO - Loaded configuration from config/config.json",
    "2023-03-15 12:35:01 - INFO - Displayed photo: static/images/photos/sunset.jpg"
  ]
}
```

## Error Handling

All API endpoints return appropriate HTTP status codes:

- `200 OK`: The request was successful
- `400 Bad Request`: The request was invalid or cannot be served
- `404 Not Found`: The resource could not be found
- `500 Internal Server Error`: An error occurred on the server

Error responses include a JSON object with an error message:

```json
{
  "error": "Error message details"
}
```

## Examples

### Updating the Rotation Interval with cURL

```bash
curl -X POST \
  http://your-pi-ip:5000/api/config \
  -H 'Content-Type: application/json' \
  -d '{"display": {"rotation_interval_minutes": 30}}'
```

### Uploading a Photo with cURL

```bash
curl -X POST \
  http://your-pi-ip:5000/api/photos \
  -F 'file=@/path/to/your/photo.jpg'
```

### Refreshing the Display with cURL

```bash
curl -X POST http://your-pi-ip:5000/api/refresh
```

## Rate Limiting

There are currently no rate limits implemented on the API. However, be considerate with request frequency, especially on the resource-constrained Raspberry Pi Zero W.