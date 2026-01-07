#!/usr/bin/env python3
"""
InkFrame - E-Ink Digital Photo Frame
Main entry point that starts both the display and web components.
"""

import argparse
import logging
import os
import signal
import sys
import threading
import time
from multiprocessing import Process

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
    handlers=[logging.StreamHandler(), logging.FileHandler("inkframe.log")],
)

logger = logging.getLogger(__name__)

# Add the project root to the Python path
project_root = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
sys.path.insert(0, project_root)

# Import application modules
from src.display.eink_simulator import EInkSimulator
from src.display.photo_manager import PhotoManager
from src.utils.config_manager import ConfigManager
from src.web.app import app as flask_app


def run_display():
    """Run the photo display component"""
    logger.info("Starting photo display manager")

    # Check if simulation mode is enabled
    config_manager = ConfigManager()
    simulation_mode = config_manager.get("system.simulation_mode", False)

    if simulation_mode:
        logger.info("Running in SIMULATION mode (no hardware)")
        # Create simulator with display type from config
        display_type = config_manager.get("display.type", "7in5_V2")
        color_mode = config_manager.get("display.color_mode", "grayscale")
        display = EInkSimulator(display_type=display_type, color_mode=color_mode)
        display.init()
        # For now, just run a test cycle in simulation mode
        # Full integration would require modifying PhotoManager to accept external display
        import time

        from PIL import Image, ImageDraw, ImageFont

        logger.info("Displaying simulation test pattern...")
        test_image = Image.new(
            "L" if color_mode != "color" else "RGB",
            (display.width, display.height),
            255 if color_mode != "color" else (255, 255, 255),
        )
        draw = ImageDraw.Draw(test_image)
        draw.text(
            (200, 240),
            "SIMULATION MODE",
            font=ImageFont.load_default(),
            fill=0 if color_mode != "color" else (0, 0, 0),
        )
        display.display_image_buffer(test_image, force_refresh=True)
        logger.info("Simulation complete. Check 'simulation/' directory for output.")
        time.sleep(60)  # Keep simulation running for 60 seconds
    else:
        # Normal mode - use PhotoManager with real hardware
        photo_manager = PhotoManager()
        photo_manager.run_photo_cycle()


def run_web(port=5000, debug=False):
    """Run the web interface component"""
    logger.info(f"Starting web interface on port {port}")
    flask_app.run(host="0.0.0.0", port=port, debug=debug)


def main():
    """Main entry point"""
    parser = argparse.ArgumentParser(description="InkFrame - E-Ink Digital Photo Frame")
    parser.add_argument(
        "--web-only", action="store_true", help="Run only the web interface"
    )
    parser.add_argument(
        "--display-only", action="store_true", help="Run only the display component"
    )
    parser.add_argument(
        "--simulation",
        action="store_true",
        help="Run in simulation mode (no hardware required)",
    )
    parser.add_argument(
        "--port", type=int, default=5000, help="Web interface port (default: 5000)"
    )
    parser.add_argument("--debug", action="store_true", help="Enable debug mode")

    args = parser.parse_args()

    # Check if configuration exists, create if not
    config_manager = ConfigManager()

    # Load configuration
    port = args.port or config_manager.get("system.web_port", 5000)
    debug = args.debug or config_manager.get("system.debug_mode", False)

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
