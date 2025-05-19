#!/usr/bin/env python3
"""
Flask web application for InkFrame.
Provides a web interface for managing photos and configuration.
"""
import os
import sys
import logging
import json
import glob
import threading
import time
from datetime import datetime
from werkzeug.utils import secure_filename

from flask import Flask, request, jsonify, render_template, send_from_directory

# Add parent directory to path for imports
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from utils.config_manager import ConfigManager
from utils.image_processor import ImageProcessor
from display.photo_manager import PhotoManager
from weather.weather_client import WeatherClient

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.StreamHandler(),
        logging.FileHandler('inkframe.log')
    ]
)

logger = logging.getLogger(__name__)

# Initialize application
app = Flask(__name__, 
           static_folder=os.path.abspath('../../static'),
           template_folder=os.path.abspath('../../static/templates'))

# Initialize components
config_manager = ConfigManager()
config = config_manager.config
image_processor = ImageProcessor(config)
weather_client = WeatherClient(config)

# Global reference to the photo manager
photo_manager = None
photo_thread = None

# Setup upload directory
UPLOAD_FOLDER = config['photos']['directory']
ALLOWED_EXTENSIONS = {'png', 'jpg', 'jpeg', 'gif', 'bmp', 'heic', 'heif'}
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER
os.makedirs(UPLOAD_FOLDER, exist_ok=True)
os.makedirs(os.path.join(UPLOAD_FOLDER, 'thumbnails'), exist_ok=True)

def allowed_file(filename):
    """Check if the file extension is allowed"""
    return '.' in filename and \
           filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

def start_photo_thread():
    """Start the photo display thread if it's not running"""
    global photo_manager, photo_thread
    
    if photo_thread is None or not photo_thread.is_alive():
        logger.info("Starting photo display thread")
        photo_manager = PhotoManager(config_path="config/config.json")
        photo_thread = threading.Thread(target=photo_manager.run_photo_cycle, daemon=True)
        photo_thread.start()
        return True
    else:
        logger.info("Photo display thread already running")
        return False

#
# Routes
#

@app.route('/')
def index():
    """Serve the main page"""
    return render_template('index.html')

@app.route('/api/photos', methods=['GET'])
def get_photos():
    """Get a list of all photos"""
    try:
        photos = []
        # Get all photos
        for ext in ALLOWED_EXTENSIONS:
            photos.extend(glob.glob(os.path.join(app.config['UPLOAD_FOLDER'], f'*.{ext}')))
        
        # Get all thumbnails
        thumbnails = {}
        for ext in ['jpg', 'jpeg', 'png']:
            for thumb in glob.glob(os.path.join(app.config['UPLOAD_FOLDER'], 'thumbnails', f'*.{ext}')):
                basename = os.path.basename(thumb)
                name = os.path.splitext(basename)[0]
                thumbnails[name] = f'/static/images/photos/thumbnails/{basename}'
        
        # Format the response
        result = []
        for photo in photos:
            basename = os.path.basename(photo)
            name = os.path.splitext(basename)[0]
            photo_url = f'/static/images/photos/{basename}'
            
            # Find matching thumbnail or use the photo itself
            thumbnail_url = thumbnails.get(name, photo_url)
            
            result.append({
                'id': name,
                'name': basename,
                'url': photo_url,
                'thumbnail': thumbnail_url,
                'date_added': datetime.fromtimestamp(os.path.getctime(photo)).isoformat()
            })
        
        # Sort by date added (newest first)
        result.sort(key=lambda x: x['date_added'], reverse=True)
        
        return jsonify({'photos': result})
    except Exception as e:
        logger.error(f"Error getting photos: {e}")
        return jsonify({'error': 'Failed to get photos'}), 500

@app.route('/api/photos', methods=['POST'])
def upload_photo():
    """Upload a new photo"""
    try:
        # Check if a file was uploaded
        if 'file' not in request.files:
            return jsonify({'error': 'No file part'}), 400
            
        file = request.files['file']
        
        # Check if a file was selected
        if file.filename == '':
            return jsonify({'error': 'No file selected'}), 400
            
        if file and allowed_file(file.filename):
            # Secure the filename to prevent path traversal
            filename = secure_filename(file.filename)
            
            # Save the uploaded file
            upload_path = os.path.join(app.config['UPLOAD_FOLDER'], 'uploads')
            os.makedirs(upload_path, exist_ok=True)
            temp_path = os.path.join(upload_path, filename)
            file.save(temp_path)
            
            # Process the image
            processed_path = image_processor.process_new_image(temp_path)
            
            if processed_path:
                return jsonify({
                    'success': True,
                    'message': 'File uploaded and processed successfully',
                    'filename': os.path.basename(processed_path)
                })
            else:
                return jsonify({'error': 'Failed to process image'}), 500
        else:
            return jsonify({'error': 'File type not allowed'}), 400
    except Exception as e:
        logger.error(f"Error uploading photo: {e}")
        return jsonify({'error': 'Failed to upload photo'}), 500

@app.route('/api/photos/<photo_id>', methods=['DELETE'])
def delete_photo(photo_id):
    """Delete a photo"""
    try:
        # Prevent path traversal
        photo_id = secure_filename(photo_id)
        
        # Find the photo file
        photo_paths = []
        for ext in ALLOWED_EXTENSIONS:
            photo_path = os.path.join(app.config['UPLOAD_FOLDER'], f'{photo_id}.{ext}')
            if os.path.exists(photo_path):
                photo_paths.append(photo_path)
        
        # Find the thumbnail
        thumb_paths = []
        for ext in ['jpg', 'jpeg', 'png']:
            thumb_path = os.path.join(app.config['UPLOAD_FOLDER'], 'thumbnails', f'{photo_id}.{ext}')
            if os.path.exists(thumb_path):
                thumb_paths.append(thumb_path)
        
        if not photo_paths:
            return jsonify({'error': 'Photo not found'}), 404
        
        # Delete the files
        for path in photo_paths + thumb_paths:
            os.remove(path)
            logger.info(f"Deleted file: {path}")
        
        return jsonify({'success': True, 'message': 'Photo deleted successfully'})
    except Exception as e:
        logger.error(f"Error deleting photo: {e}")
        return jsonify({'error': 'Failed to delete photo'}), 500

@app.route('/api/refresh', methods=['POST'])
def refresh_display():
    """Manually refresh the display with a new photo"""
    try:
        global photo_manager
        
        # If photo manager isn't running, start it
        if not photo_manager:
            photo_manager = PhotoManager(config_path="config/config.json")
        
        # Display a new random photo
        success = photo_manager.display_photo()
        
        if success:
            return jsonify({'success': True, 'message': 'Display refreshed with a new photo'})
        else:
            return jsonify({'error': 'Failed to refresh display'}), 500
    except Exception as e:
        logger.error(f"Error refreshing display: {e}")
        return jsonify({'error': 'Failed to refresh display'}), 500

@app.route('/api/config', methods=['GET'])
def get_config():
    """Get the current configuration"""
    try:
        # Return a sanitized version of the config (remove sensitive info)
        config = config_manager.config.copy()
        
        # Mask API key if present
        if 'weather' in config and 'api_key' in config['weather'] and config['weather']['api_key']:
            masked_key = config['weather']['api_key'][:4] + '****'
            config['weather']['api_key'] = masked_key
        
        return jsonify({'config': config})
    except Exception as e:
        logger.error(f"Error getting configuration: {e}")
        return jsonify({'error': 'Failed to get configuration'}), 500

@app.route('/api/config', methods=['POST'])
def update_config():
    """Update the configuration"""
    try:
        # Get the updated configuration
        updates = request.json
        
        if not updates:
            return jsonify({'error': 'No updates provided'}), 400
        
        # Update the configuration
        success = config_manager.update_config(updates)
        
        if success:
            # Reload components with new configuration
            global config, image_processor, weather_client
            config = config_manager.config
            image_processor = ImageProcessor(config)
            weather_client = WeatherClient(config)
            
            return jsonify({'success': True, 'message': 'Configuration updated successfully'})
        else:
            return jsonify({'error': 'Failed to update configuration'}), 500
    except Exception as e:
        logger.error(f"Error updating configuration: {e}")
        return jsonify({'error': 'Failed to update configuration'}), 500

@app.route('/api/weather', methods=['GET'])
def get_weather():
    """Get the current weather"""
    try:
        weather = weather_client.get_current_weather()
        
        if weather:
            return jsonify({'weather': weather})
        else:
            return jsonify({'error': 'Failed to get weather data'}), 500
    except Exception as e:
        logger.error(f"Error getting weather: {e}")
        return jsonify({'error': 'Failed to get weather data'}), 500

@app.route('/api/weather/refresh', methods=['POST'])
def refresh_weather():
    """Force refresh the weather data"""
    try:
        weather = weather_client.get_current_weather(force_refresh=True)
        
        if weather:
            return jsonify({'weather': weather, 'message': 'Weather data refreshed'})
        else:
            return jsonify({'error': 'Failed to refresh weather data'}), 500
    except Exception as e:
        logger.error(f"Error refreshing weather: {e}")
        return jsonify({'error': 'Failed to refresh weather data'}), 500

@app.route('/api/system/status', methods=['GET'])
def get_system_status():
    """Get system status information"""
    try:
        # Get disk usage
        total, used, free = 0, 0, 0
        try:
            import shutil
            total, used, free = shutil.disk_usage('/')
        except:
            pass
        
        # Get uptime
        uptime = 0
        try:
            with open('/proc/uptime', 'r') as f:
                uptime = float(f.readline().split()[0])
        except:
            pass
        
        # Get CPU temperature (Raspberry Pi specific)
        cpu_temp = 'N/A'
        try:
            with open('/sys/class/thermal/thermal_zone0/temp', 'r') as f:
                cpu_temp = str(float(f.read()) / 1000) + '°C'
        except:
            pass
        
        # Check if display thread is running
        display_running = photo_thread is not None and photo_thread.is_alive()
        
        # Format disk space
        def format_size(size_bytes):
            if size_bytes == 0:
                return "0B"
            size_name = ("B", "KB", "MB", "GB", "TB")
            i = 0
            while size_bytes >= 1024 and i < len(size_name) - 1:
                size_bytes /= 1024
                i += 1
            return f"{size_bytes:.2f} {size_name[i]}"
        
        status = {
            'disk': {
                'total': format_size(total),
                'used': format_size(used),
                'free': format_size(free),
                'percent_used': round(used / total * 100, 1) if total > 0 else 0
            },
            'uptime': uptime,
            'cpu_temp': cpu_temp,
            'display_running': display_running,
            'photo_count': len(glob.glob(os.path.join(app.config['UPLOAD_FOLDER'], '*.*'))),
            'timestamp': datetime.now().isoformat()
        }
        
        return jsonify({'status': status})
    except Exception as e:
        logger.error(f"Error getting system status: {e}")
        return jsonify({'error': 'Failed to get system status'}), 500

@app.route('/api/system/start', methods=['POST'])
def start_display():
    """Start the photo display service"""
    try:
        success = start_photo_thread()
        
        if success:
            return jsonify({'success': True, 'message': 'Display service started'})
        else:
            return jsonify({'success': True, 'message': 'Display service already running'})
    except Exception as e:
        logger.error(f"Error starting display service: {e}")
        return jsonify({'error': 'Failed to start display service'}), 500

@app.route('/api/system/logs', methods=['GET'])
def get_logs():
    """Get the application logs"""
    try:
        lines = request.args.get('lines', default=100, type=int)
        
        if os.path.exists('inkframe.log'):
            with open('inkframe.log', 'r') as f:
                log_lines = f.readlines()
                # Get the last N lines
                log_lines = log_lines[-lines:]
                
            return jsonify({'logs': log_lines})
        else:
            return jsonify({'logs': []})
    except Exception as e:
        logger.error(f"Error getting logs: {e}")
        return jsonify({'error': 'Failed to get logs'}), 500

# Start the application
if __name__ == '__main__':
    # Start the photo display thread
    start_photo_thread()
    
    # Start the Flask application
    port = config['system'].get('web_port', 5000)
    debug = config['system'].get('debug_mode', False)
    
    logger.info(f"Starting web server on port {port}")
    app.run(host='0.0.0.0', port=port, debug=debug)