#!/usr/bin/env python3
"""
InkFrame - E-Ink Digital Photo Frame
Main entry point that starts both the display and web components.
"""
import os
import sys
import logging
import argparse
import time
import threading
import signal
from multiprocessing import Process

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

# Add the project root to the Python path
project_root = os.path.abspath(os.path.join(os.path.dirname(__file__), '..'))
sys.path.insert(0, project_root)

# Import application modules
from utils.config_manager import ConfigManager
from display.photo_manager import PhotoManager
from web.app import app as flask_app

def run_display():
    """Run the photo display component"""
    logger.info("Starting photo display manager")
    photo_manager = PhotoManager()
    photo_manager.run_photo_cycle()

def run_web(port=5000, debug=False):
    """Run the web interface component"""
    logger.info(f"Starting web interface on port {port}")
    flask_app.run(host='0.0.0.0', port=port, debug=debug)

def main():
    """Main entry point"""
    parser = argparse.ArgumentParser(description='InkFrame - E-Ink Digital Photo Frame')
    parser.add_argument('--web-only', action='store_true', help='Run only the web interface')
    parser.add_argument('--display-only', action='store_true', help='Run only the display component')
    parser.add_argument('--port', type=int, default=5000, help='Web interface port (default: 5000)')
    parser.add_argument('--debug', action='store_true', help='Enable debug mode')
    
    args = parser.parse_args()
    
    # Check if configuration exists, create if not
    config_manager = ConfigManager()
    
    # Load configuration
    port = args.port or config_manager.get('system.web_port', 5000)
    debug = args.debug or config_manager.get('system.debug_mode', False)
    
    # Track running processes
    processes = []
    
    # Setup signal handling for graceful shutdown
    def signal_handler(sig, frame):
        logger.info("Shutdown signal received, terminating processes...")
        for process in processes:
            if process.is_alive():
                process.terminate()
        sys.exit(0)
    
    signal.signal(signal.SIGINT, signal_handler)
    signal.signal(signal.SIGTERM, signal_handler)
    
    try:
        # Run components based on arguments
        if args.web_only:
            # Run only the web interface
            run_web(port, debug)
        elif args.display_only:
            # Run only the display component
            run_display()
        else:
            # Run both components in separate processes
            web_process = Process(target=run_web, args=(port, debug))
            web_process.start()
            processes.append(web_process)
            
            display_process = Process(target=run_display)
            display_process.start()
            processes.append(display_process)
            
            # Keep the main process running to handle signals
            while all(p.is_alive() for p in processes):
                time.sleep(1)
            
            # If we get here, one of the processes died
            for process in processes:
                if not process.is_alive():
                    logger.error(f"Process {process.name} died unexpectedly")
                    process.join()
                else:
                    process.terminate()
            
            sys.exit(1)
    
    except Exception as e:
        logger.error(f"Error in main process: {e}")
        for process in processes:
            if process.is_alive():
                process.terminate()
        sys.exit(1)

if __name__ == "__main__":
    main()