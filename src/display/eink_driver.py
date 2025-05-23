#!/usr/bin/env python3
"""
E-Ink display driver for Waveshare e-ink displays.
Handles initialization, display updates, and cleanup.

Features:
- Supports multiple display types: B&W, grayscale, and 7-color ACeP
- Handles full and partial refresh modes
- Provides simulation mode for development without hardware
- Built-in error handling and graceful degradation
- Power management for optimal battery life
"""
import os
import sys
import logging
import time

# This try/except allows for development on non-Raspberry Pi systems
try:
    # For Waveshare e-Paper HAT
    import importlib
    
    # Define supported display drivers
    SUPPORTED_DRIVERS = {
        "7in5_V2": "epd7in5_V2",   # 7.5 inch B/W V2 (800×480)
        "7in3f": "epd7in3f"        # 7.3 inch ACeP 7-color (800×480)
    }
    
    # Try to import available drivers
    display_modules = {}
    for key, module_name in SUPPORTED_DRIVERS.items():
        try:
            display_modules[key] = importlib.import_module(f"waveshare_epd.{module_name}")
        except ImportError:
            logging.warning(f"Could not import {module_name}")
    
    SIMULATION_MODE = len(display_modules) == 0
    
    if SIMULATION_MODE:
        logging.warning("No Waveshare EPD drivers found, running in simulation mode")
    else:
        logging.info(f"Found {len(display_modules)} Waveshare EPD drivers: {list(display_modules.keys())}")
except ImportError:
    logging.warning("Waveshare EPD library not found, running in simulation mode")
    SIMULATION_MODE = True
    display_modules = {}

from PIL import Image, ImageDraw, ImageFont, ImageOps

logger = logging.getLogger(__name__)

class EInkDisplay:
    """Driver for Waveshare e-Paper HAT displays
    
    This class provides an interface to Waveshare e-Paper displays.
    It supports black & white, grayscale, and 7-color modes, as well as full and
    partial refresh patterns for optimal display quality and speed.
    """
    
    def __init__(self, display_type="7in5_V2", color_mode="grayscale"):
        """Initialize the display
        
        Args:
            display_type (str): The display type to use ("7in5_V2" or "7in3f")
            color_mode (str): The color mode to use ("bw", "grayscale", or "color")
        """
        self.width = 800
        self.height = 480
        self.epd = None
        self.initialized = False
        self.display_type = display_type
        self.color_mode = color_mode
        self.is_color_display = display_type == "7in3f"  # 7in3f is the 7-color ACeP display
        self.last_full_refresh = 0  # Timestamp of last full refresh
        self.refresh_count = 0  # Count of partial refreshes since last full refresh
        
        # For backwards compatibility
        self.grayscale_mode = color_mode == "grayscale"
        
        if not SIMULATION_MODE:
            try:
                # Get the appropriate display module
                if display_type in display_modules:
                    module = display_modules[display_type]
                    self.epd = module.EPD()
                    self.init_display()
                    self.initialized = True
                else:
                    available = list(display_modules.keys())
                    logger.error(f"Display type {display_type} not found. Available types: {available}")
                    self.initialized = False
            except Exception as e:
                logger.error(f"Failed to initialize display: {e}")
                self.initialized = False
        else:
            # Create a simulation directory if it doesn't exist
            os.makedirs('simulation', exist_ok=True)
            logger.info("Running in simulation mode")
            self.initialized = True
    
    def init_display(self):
        """Initialize the e-Paper display"""
        try:
            logger.info("Initializing display")
            self.epd.init()
            return True
        except Exception as e:
            logger.error(f"Error initializing display: {e}")
            return False
    
    def clear(self):
        """Clear the display to white"""
        if SIMULATION_MODE:
            logger.info("Simulation: Clearing display")
            return True
            
        if not self.initialized:
            logger.warning("Display not initialized, attempting to initialize before clear")
            if not self.init_display():
                return False
            
        try:
            logger.info("Clearing display (this may take ~35 seconds)...")
            # Some displays need to be woken up before clearing
            if hasattr(self.epd, 'init'):
                self.epd.init()
            self.epd.Clear()
            logger.info("Display cleared")
            return True
        except Exception as e:
            logger.error(f"Error clearing display: {e}")
            return False
    
    def display_image(self, image_path, force_full_refresh=False):
        """Display an image on the e-Paper display
        
        Args:
            image_path (str): Path to the image file
            force_full_refresh (bool): Whether to force a full refresh regardless of history
            
        Returns:
            bool: True if successful, False otherwise
        """
        if not os.path.exists(image_path):
            logger.error(f"Image not found: {image_path}")
            return False
            
        try:
            # Open the image
            image = Image.open(image_path)
            return self.display_image_buffer(image, force_full_refresh)
            
        except Exception as e:
            logger.error(f"Error displaying image {image_path}: {e}")
            return False
    
    def display_image_buffer(self, image, force_full_refresh=False):
        """Display a PIL Image object directly
        
        Args:
            image (Image): PIL Image object to display
            force_full_refresh (bool): Whether to force a full refresh regardless of history
            
        Returns:
            bool: True if successful, False otherwise
        """
        try:
            # Ensure image is right size
            if image.size != (self.width, self.height):
                image = image.resize((self.width, self.height))
            
            # Apply image processing based on display type and color mode
            if self.is_color_display:
                # For 7-color ACeP display
                if image.mode != 'RGB' and image.mode != 'RGBA':
                    image = image.convert('RGB')
                # No need to convert to palette mode here; the display driver does that
            elif self.color_mode == "grayscale":
                # For 4-level grayscale mode
                if image.mode != 'L':
                    image = image.convert('L')  # Convert to grayscale
            else:
                # For 1-bit black and white mode
                if image.mode != '1':
                    image = image.convert('1')
            
            # Handle simulation mode
            if SIMULATION_MODE:
                # In simulation mode, save the image that would be displayed
                os.makedirs('simulation', exist_ok=True)
                sim_path = os.path.join('simulation', 'current_display.png')
                image.save(sim_path)
                logger.info(f"Simulation: Image buffer displayed and saved to {sim_path}")
                return True
            
            # Check if we need to do a full refresh
            current_time = time.time()
            needs_full_refresh = force_full_refresh or \
                               self.refresh_count >= 5 or \
                               (current_time - self.last_full_refresh) > 3600  # 1 hour
            
            # Display the image with appropriate refresh mode based on display type and color mode
            if self.is_color_display:  # 7.3 inch ACeP 7-color display
                logger.info("Displaying on 7-color ACeP display")
                logger.debug(f"Image before display: mode={image.mode}, size={image.size}")
                
                # TEMPORARILY DISABLED: Let's see if inversion is the problem
                # The 7in3f driver seems to invert colors, so we need to invert them first
                # But we need to ensure the image stays in RGB mode
                if False and image.mode == 'RGB':
                    # For RGB images, invert each channel separately to preserve color
                    r, g, b = image.split()
                    from PIL import ImageOps
                    r = ImageOps.invert(r)
                    g = ImageOps.invert(g)
                    b = ImageOps.invert(b)
                    image = Image.merge('RGB', (r, g, b))
                    logger.debug("Inverted RGB image colors to compensate for driver inversion")
                else:
                    logger.debug(f"NOT inverting image, mode={image.mode}")
                
                # ACeP displays always need a full refresh
                self.epd.display(self.epd.getbuffer(image))
                self.last_full_refresh = current_time
                self.refresh_count = 0
            else:  # 7.5 inch black/white or grayscale display
                if needs_full_refresh:
                    logger.info("Performing full refresh")
                    if self.color_mode == "grayscale":
                        self.epd.display_4Gray(self.epd.getbuffer_4Gray(image))
                    else:
                        self.epd.display(self.epd.getbuffer(image))
                    self.last_full_refresh = current_time
                    self.refresh_count = 0
                else:
                    logger.info("Performing partial refresh")
                    if self.color_mode == "grayscale":
                        # Some e-Paper displays don't support partial refresh in grayscale mode
                        # Fall back to full refresh in grayscale mode
                        self.epd.display_4Gray(self.epd.getbuffer_4Gray(image))
                    else:
                        # Use partial refresh for black/white mode
                        self.epd.display_Partial(self.epd.getbuffer(image))
                    self.refresh_count += 1
            
            logger.info("Displayed image from buffer")
            return True
            
        except Exception as e:
            logger.error(f"Error displaying image buffer: {e}")
            # Try to recover if possible
            if not self.initialized:
                logger.info("Attempting to reinitialize display")
                try:
                    self.init_display()
                except:
                    pass
            return False
    
    def sleep(self):
        """Put the display to sleep to conserve power"""
        if SIMULATION_MODE:
            logger.info("Simulation: Display set to sleep mode")
            return True
            
        if not self.initialized:
            return False
            
        try:
            logger.info("Setting display to sleep mode")
            self.epd.sleep()
            return True
        except Exception as e:
            logger.error(f"Error putting display to sleep: {e}")
            return False
    
    def close(self):
        """Clean up resources and shut down display"""
        if SIMULATION_MODE:
            logger.info("Simulation: Display resources released")
            return True
            
        if not self.initialized:
            return False
            
        try:
            logger.info("Closing display")
            # The 7in3f driver doesn't have Dev_exit, just pass
            if hasattr(self.epd, 'Dev_exit'):
                self.epd.Dev_exit()
            return True
        except Exception as e:
            logger.error(f"Error closing display: {e}")
            return False

    def perform_diagnostic(self):
        """Run a display diagnostic pattern to help identify issues
        
        Returns:
            bool: True if successful, False otherwise
        """
        try:
            if SIMULATION_MODE:
                logger.info("Simulation: Running display diagnostic")
                
                # Create diagnostic images and save them to simulation folder
                patterns = []
                
                # Pattern 1: All white
                img1 = Image.new('1', (self.width, self.height), 255)
                patterns.append((img1, "diag_white.png"))
                
                # Pattern 2: All black
                img2 = Image.new('1', (self.width, self.height), 0)
                patterns.append((img2, "diag_black.png"))
                
                # Pattern 3: Checkerboard
                img3 = Image.new('1', (self.width, self.height), 255)
                draw = ImageDraw.Draw(img3)
                square_size = 50
                for y in range(0, self.height, square_size):
                    for x in range(0, self.width, square_size):
                        if (x // square_size + y // square_size) % 2 == 0:
                            draw.rectangle([(x, y), (x + square_size - 1, y + square_size - 1)], fill=0)
                patterns.append((img3, "diag_checkerboard.png"))
                
                # Pattern 4: Gradient (for grayscale)
                if self.grayscale_mode:
                    img4 = Image.new('L', (self.width, self.height), 255)
                    draw = ImageDraw.Draw(img4)
                    for x in range(self.width):
                        gray_value = int(255 * (1 - x / self.width))
                        draw.line([(x, 0), (x, self.height)], fill=gray_value)
                    patterns.append((img4, "diag_gradient.png"))
                
                # Save all patterns
                for img, filename in patterns:
                    img.save(os.path.join('simulation', filename))
                
                return True
            
            # On real hardware
            logger.info("Running display diagnostic")
            
            # Clear to white
            self.clear()
            time.sleep(1)
            
            # Display all black
            black_img = Image.new('1', (self.width, self.height), 0)
            if self.grayscale_mode:
                self.epd.display_4Gray(self.epd.getbuffer_4Gray(black_img))
            else:
                self.epd.display(self.epd.getbuffer(black_img))
            time.sleep(1)
            
            # Display checkerboard pattern
            check_img = Image.new('1', (self.width, self.height), 255)
            draw = ImageDraw.Draw(check_img)
            square_size = 50
            for y in range(0, self.height, square_size):
                for x in range(0, self.width, square_size):
                    if (x // square_size + y // square_size) % 2 == 0:
                        draw.rectangle([(x, y), (x + square_size - 1, y + square_size - 1)], fill=0)
                        
            if self.grayscale_mode:
                self.epd.display_4Gray(self.epd.getbuffer_4Gray(check_img))
            else:            
                self.epd.display(self.epd.getbuffer(check_img))
            time.sleep(1)
            
            # Clear to finish
            self.clear()
            
            return True
            
        except Exception as e:
            logger.error(f"Error running display diagnostic: {e}")
            return False

if __name__ == "__main__":
    # Simple test when run directly
    logging.basicConfig(level=logging.INFO)
    
    # Parse command line arguments for display type and color mode
    import argparse
    parser = argparse.ArgumentParser(description="Test the e-ink display")
    parser.add_argument("--display", choices=["7in5_V2", "7in3f"], default="7in5_V2", help="Display type")
    parser.add_argument("--mode", choices=["bw", "grayscale", "color"], default="grayscale", help="Color mode")
    args = parser.parse_args()
    
    # Create display with specified type and mode
    display = EInkDisplay(display_type=args.display, color_mode=args.mode)
    
    # Create a test image based on the display type and color mode
    if display.is_color_display:  # 7.3 inch ACeP 7-color display
        # Create a color test image
        image = Image.new('RGB', (display.width, display.height), (255, 255, 255))  # White background
        draw = ImageDraw.Draw(image)
        
        # Draw color blocks
        colors = [
            (0, 0, 0),      # Black
            (255, 0, 0),    # Red
            (0, 255, 0),    # Green
            (0, 0, 255),    # Blue
            (255, 255, 0),  # Yellow
            (255, 128, 0)   # Orange
        ]
        
        block_width = display.width // len(colors)
        for i, color in enumerate(colors):
            x1 = i * block_width
            x2 = (i + 1) * block_width
            draw.rectangle([(x1, 100), (x2, 300)], fill=color)
        
        # Draw text
        font = ImageFont.truetype("FreeSans.ttf", 60) if os.path.exists("/usr/share/fonts/truetype/freefont/FreeSans.ttf") else ImageFont.load_default()
        draw.text((150, 350), "7-Color E-Paper!", font=font, fill=(0, 0, 0))
        
    elif display.color_mode == "grayscale":  # Grayscale mode
        image = Image.new('L', (display.width, display.height), 255)  # 255: white
        draw = ImageDraw.Draw(image)
        
        # Draw gradient background
        for x in range(display.width):
            gray_value = int(200 + 55 * (x / display.width))
            draw.line([(x, 0), (x, display.height)], fill=gray_value)
        
        # Draw darker rectangle in center
        draw.rectangle([(100, 100), (display.width - 100, display.height - 100)], outline=0)
        
        # Draw some text
        font = ImageFont.truetype("FreeSans.ttf", 60) if os.path.exists("/usr/share/fonts/truetype/freefont/FreeSans.ttf") else ImageFont.load_default()
        draw.text((150, 200), "Hello E-Paper!", font=font, fill=50)  # Dark gray text
        
    else:  # Black and white mode
        image = Image.new('1', (display.width, display.height), 255)  # 255: white
        draw = ImageDraw.Draw(image)
        draw.rectangle([(0, 0), (display.width - 1, display.height - 1)], outline=0)
        font = ImageFont.truetype("FreeSans.ttf", 60) if os.path.exists("/usr/share/fonts/truetype/freefont/FreeSans.ttf") else ImageFont.load_default()
        draw.text((200, 200), "Hello E-Paper!", font=font, fill=0)
    
    # Display the test image
    display.display_image_buffer(image)
    
    # Wait 2 seconds
    time.sleep(2)
    
    # Run diagnostic patterns
    if "-d" in sys.argv or "--diagnostic" in sys.argv:
        display.perform_diagnostic()
    
    # Clean up
    display.sleep()
    display.close()