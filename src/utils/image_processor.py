#!/usr/bin/env python3
"""
Image processor for InkFrame.
Handles image conversion, resizing, and optimization for e-ink display.

Features:
- Converts images to optimal format for e-ink display
- Supports 1-bit (black/white), 4-level grayscale, and 7-color ACeP modes
- Enhances contrast and brightness for better e-ink visibility
- Multiple dithering algorithms for improved visual quality
- Handles HEIC format conversion via ImageMagick
- Generates thumbnails for the web interface
- Various preprocessing filters for optimal e-ink display
"""
import os
import sys
import logging
import subprocess
from PIL import Image, ImageOps, ImageEnhance, ImageFilter

logger = logging.getLogger(__name__)

class ImageProcessor:
    """Processes images for optimal display on e-ink screens
    
    This class provides utilities for converting and optimizing images
    for display on e-ink screens, which have specific requirements and
    limitations compared to traditional displays.
    """
    
    def __init__(self, config):
        """Initialize the image processor with configuration
        
        Args:
            config (dict): Application configuration dictionary
        """
        self.config = config
        self.max_width = config["photos"]["max_width"]
        self.max_height = config["photos"]["max_height"]
        self.enable_dithering = config["display"].get("enable_dithering", True)
        self.output_format = config["photos"].get("format", "bmp").lower()
        self.color_mode = config["display"].get("color_mode", "grayscale")
        self.grayscale_mode = self.color_mode == "grayscale"  # For backward compatibility
        self.dithering_method = config["display"].get("dithering_method", "floydsteinberg")
        self.contrast_factor = config["display"].get("contrast_factor", 1.5)
        self.brightness_factor = config["display"].get("brightness_factor", 1.2)
        self.sharpness_factor = config["display"].get("sharpness_factor", 1.3)
        
        # Ensure the photo directory exists
        self.photo_dir = config["photos"]["directory"]
        os.makedirs(self.photo_dir, exist_ok=True)
        
        # Map dithering method names to PIL constants
        self.dithering_methods = {
            "none": None,
            "floydsteinberg": Image.Dither.FLOYDSTEINBERG,
            "ordered": Image.Dither.ORDERED,
            "rasterize": Image.Dither.RASTERIZE
        }
        
        # Define the 7-color palette for ACeP display
        self.acep_colors = [
            (0, 0, 0),      # Black
            (255, 255, 255), # White
            (0, 255, 0),    # Green
            (0, 0, 255),    # Blue
            (255, 0, 0),    # Red
            (255, 255, 0),  # Yellow
            (255, 128, 0)   # Orange
        ]
    
    def _has_imagemagick(self):
        """Check if ImageMagick is installed"""
        try:
            result = subprocess.run(['convert', '-version'], 
                                   stdout=subprocess.PIPE, 
                                   stderr=subprocess.PIPE, 
                                   text=True,
                                   check=False)
            return result.returncode == 0
        except FileNotFoundError:
            return False
    
    def _convert_heic(self, input_path, output_path):
        """Convert HEIC to another format using ImageMagick"""
        try:
            if not self._has_imagemagick():
                logger.error("ImageMagick not installed, can't convert HEIC files")
                return None
                
            # Convert using ImageMagick
            result = subprocess.run(['convert', input_path, output_path], 
                                   stdout=subprocess.PIPE, 
                                   stderr=subprocess.PIPE, 
                                   text=True,
                                   check=True)
            
            if result.returncode == 0:
                logger.info(f"Converted HEIC file: {input_path} -> {output_path}")
                return output_path
            else:
                logger.error(f"Error converting HEIC file: {result.stderr}")
                return None
        except Exception as e:
            logger.error(f"Error during HEIC conversion: {e}")
            return None
    
    def preprocess_image(self, input_path, output_path=None, mode=None):
        """
        Preprocess an image for e-ink display:
        1. Convert HEIC if needed
        2. Resize to fit display
        3. Apply image enhancement (contrast, brightness, sharpness)
        4. Apply optional filters for better e-ink visibility
        5. Convert to appropriate format (B&W, grayscale, or color) with optional dithering
        
        Args:
            input_path (str): Path to input image file
            output_path (str, optional): Path to save processed image
            mode (str, optional): Override processing mode ('bw', 'grayscale', or 'color')
            
        Returns:
            str: Path to processed image, or None if processing failed
        """
        try:
            # Handle HEIC files
            if input_path.lower().endswith(('.heic', '.heif')):
                temp_path = input_path.rsplit('.', 1)[0] + '.png'
                input_path = self._convert_heic(input_path, temp_path) or input_path
            
            # Open the image
            image = Image.open(input_path)
            
            # Generate output path if not provided
            if not output_path:
                filename = os.path.basename(input_path)
                name, _ = os.path.splitext(filename)
                output_path = os.path.join(self.photo_dir, f"{name}.{self.output_format}")
            
            # Resize while maintaining aspect ratio
            image_ratio = image.width / image.height
            target_ratio = self.max_width / self.max_height
            
            if image_ratio > target_ratio:
                # Image is wider than target ratio
                new_width = self.max_width
                new_height = int(self.max_width / image_ratio)
            else:
                # Image is taller than target ratio
                new_height = self.max_height
                new_width = int(self.max_height * image_ratio)
                
            image = image.resize((new_width, new_height), Image.Resampling.LANCZOS)
            
            # Process based on mode (color, grayscale, or black & white)
            process_mode = mode if mode else self.color_mode
            
            if process_mode == 'color':
                # Keep as RGB for color processing
                if image.mode != 'RGB':
                    image = image.convert('RGB')
                    
                # Apply color-appropriate enhancements
                image = self._enhance_color_image(image)
                
                # Process for 7-color ACeP display
                processed_image = self._process_color(image)
            else:
                # Convert to grayscale for B&W or grayscale processing
                image = image.convert('L')
                
                # Apply image enhancements for better e-ink visibility
                image = self._enhance_image(image)
                
                # Apply additional filtering to improve appearance on e-ink
                image = self._apply_eink_optimizations(image)
                
                if process_mode == 'grayscale':
                    # Process for 4-level grayscale mode
                    processed_image = self._process_grayscale(image)
                else:
                    # Process for 1-bit black and white mode
                    processed_image = self._process_black_white(image)
            
            # Save the processed image
            processed_image.save(output_path)
            logger.info(f"Preprocessed image saved: {output_path}")
            
            return output_path
            
        except Exception as e:
            logger.error(f"Error preprocessing image: {e}")
            return None
    
    def _enhance_image(self, image):
        """Apply image enhancements for better e-ink display
        
        Args:
            image (PIL.Image): Image to enhance
            
        Returns:
            PIL.Image: Enhanced image
        """
        # Enhance contrast
        if self.contrast_factor != 1.0:
            enhancer = ImageEnhance.Contrast(image)
            image = enhancer.enhance(self.contrast_factor)
        
        # Enhance brightness
        if self.brightness_factor != 1.0:
            enhancer = ImageEnhance.Brightness(image)
            image = enhancer.enhance(self.brightness_factor)
        
        # Enhance sharpness
        if self.sharpness_factor != 1.0:
            enhancer = ImageEnhance.Sharpness(image)
            image = enhancer.enhance(self.sharpness_factor)
            
        return image
    
    def _apply_eink_optimizations(self, image):
        """Apply optimizations specific to e-ink displays
        
        Args:
            image (PIL.Image): Image to optimize
            
        Returns:
            PIL.Image: Optimized image
        """
        # Apply a slight unsharp mask to improve perceived sharpness
        image = image.filter(ImageFilter.UnsharpMask(radius=1.5, percent=150, threshold=3))
        
        return image
    
    def _process_grayscale(self, image):
        """Process image for 4-level grayscale e-ink display
        
        Args:
            image (PIL.Image): Grayscale image to process
            
        Returns:
            PIL.Image: Processed image for 4-level grayscale
        """
        # For 4-level grayscale, we quantize the image to 4 levels
        # This approximates what the e-ink display can show
        
        # If dithering is enabled, use PIL's quantize with dithering
        if self.enable_dithering:
            # Convert to P mode with 4 colors and dithering
            palette_image = Image.new('P', (16, 16))
            palette_data = [0, 0, 0] * 1  # Black
            palette_data += [85, 85, 85] * 1  # Dark gray
            palette_data += [170, 170, 170] * 1  # Light gray
            palette_data += [255, 255, 255] * 252  # White and padding
            palette_image.putpalette(palette_data)
            
            dither_method = self.dithering_methods.get(self.dithering_method)
            image = image.quantize(colors=4, palette=palette_image, dither=dither_method)
            
            # Convert back to grayscale
            image = image.convert('L')
        else:
            # Manual quantization without dithering
            lut = [0] * 64 + [85] * 64 + [170] * 64 + [255] * 64
            image = image.point(lambda p: lut[min(255, p) // 4])
        
        return image
    
    def _enhance_color_image(self, image):
        """Apply image enhancements for color e-ink display
        
        Args:
            image (PIL.Image): Color image to enhance
            
        Returns:
            PIL.Image: Enhanced color image
        """
        # Enhance contrast
        if self.contrast_factor != 1.0:
            enhancer = ImageEnhance.Contrast(image)
            image = enhancer.enhance(self.contrast_factor)
        
        # Enhance saturation (for color displays, slightly increased saturation helps)
        enhancer = ImageEnhance.Color(image)
        image = enhancer.enhance(1.3)  # Slightly boost colors
        
        # Enhance brightness
        if self.brightness_factor != 1.0:
            enhancer = ImageEnhance.Brightness(image)
            image = enhancer.enhance(self.brightness_factor)
        
        # Enhance sharpness
        if self.sharpness_factor != 1.0:
            enhancer = ImageEnhance.Sharpness(image)
            image = enhancer.enhance(self.sharpness_factor)
            
        return image

    def _process_color(self, image):
        """Process image for 7-color ACeP e-ink display
        
        Args:
            image (PIL.Image): RGB image to process
            
        Returns:
            PIL.Image: Processed image for 7-color ACeP display
        """
        # For the 7-color display, we should NOT quantize to the palette
        # The Waveshare driver expects a full RGB image and will handle the color mapping
        # Quantizing here causes color inversion issues
        
        # Just ensure it's RGB and return it
        if image.mode != 'RGB':
            image = image.convert('RGB')
        
        return image
    
    def _process_black_white(self, image):
        """Process image for 1-bit black and white e-ink display
        
        Args:
            image (PIL.Image): Grayscale image to process
            
        Returns:
            PIL.Image: Processed image for 1-bit display
        """
        # Apply dithering if enabled
        if self.enable_dithering:
            dither_method = self.dithering_methods.get(self.dithering_method)
            # Convert to 1-bit black and white with selected dithering method
            image = image.convert('1', dither=dither_method)
        else:
            # Threshold conversion without dithering
            threshold = self.config["display"].get("threshold", 128)  # Configurable threshold
            image = image.point(lambda p: 255 if p > threshold else 0)
            image = image.convert('1')
        
        return image
    
    def generate_thumbnail(self, input_path, output_path=None, size=(200, 200)):
        """Generate a thumbnail for the web interface"""
        try:
            # Handle HEIC files
            if input_path.lower().endswith(('.heic', '.heif')):
                temp_path = input_path.rsplit('.', 1)[0] + '.png'
                input_path = self._convert_heic(input_path, temp_path) or input_path
                
            # Open the image
            image = Image.open(input_path)
            
            # Generate output path if not provided
            if not output_path:
                filename = os.path.basename(input_path)
                name, _ = os.path.splitext(filename)
                thumb_dir = os.path.join(self.photo_dir, "thumbnails")
                os.makedirs(thumb_dir, exist_ok=True)
                output_path = os.path.join(thumb_dir, f"{name}.jpg")
            
            # Create thumbnail
            image.thumbnail(size, Image.Resampling.LANCZOS)
            
            # Save the thumbnail (use JPEG for web thumbnails)
            image.convert('RGB').save(output_path, format="JPEG", quality=85)
            logger.info(f"Thumbnail generated: {output_path}")
            
            return output_path
            
        except Exception as e:
            logger.error(f"Error generating thumbnail: {e}")
            return None
    
    def process_new_image(self, input_path):
        """Process a newly uploaded image and generate its thumbnail"""
        # Preprocess for e-ink display
        output_path = self.preprocess_image(input_path)
        
        # Generate thumbnail for web interface
        if output_path:
            self.generate_thumbnail(input_path)
            
        return output_path

    def apply_specialty_filter(self, image, filter_type='sketch'):
        """Apply a specialty filter to the image for artistic effects
        
        Args:
            image (PIL.Image): Image to filter
            filter_type (str): Type of filter to apply ('sketch', 'edges', 'emboss', etc.)
            
        Returns:
            PIL.Image: Filtered image
        """
        if isinstance(image, str):
            # If a path was passed, load the image
            image = Image.open(image)
        
        if filter_type == 'sketch':
            # Create a sketch-like effect good for e-ink
            image = image.convert('L')  # Ensure grayscale
            image = ImageOps.invert(image)  # Invert
            image = image.filter(ImageFilter.FIND_EDGES)  # Find edges
            image = image.filter(ImageFilter.SMOOTH)  # Smooth slightly
            image = ImageOps.invert(image)  # Invert back
            
        elif filter_type == 'edges':
            # Emphasize edges, good for clarity on e-ink
            image = image.convert('L')  # Ensure grayscale
            image = image.filter(ImageFilter.FIND_EDGES)
            image = ImageOps.invert(image)  # Invert for white background
            
        elif filter_type == 'emboss':
            # Create an embossed effect
            image = image.convert('L')  # Ensure grayscale
            image = image.filter(ImageFilter.EMBOSS)
            image = ImageOps.autocontrast(image)  # Improve contrast
            
        elif filter_type == 'posterize':
            # Reduce to fewer colors, good for e-ink
            image = image.convert('L')  # Ensure grayscale
            # Create a custom LUT for posterization
            lut = [0] * 64 + [85] * 64 + [170] * 64 + [255] * 64
            image = image.point(lambda p: lut[min(255, p) // 4])
            
        return image

if __name__ == "__main__":
    # Simple test when run directly
    logging.basicConfig(level=logging.INFO)
    
    # Minimal test config
    config = {
        "display": {
            "enable_dithering": True,
            "color_mode": "grayscale",  # 'bw', 'grayscale', or 'color'
            "dithering_method": "floydsteinberg",
            "contrast_factor": 1.5,
            "brightness_factor": 1.2,
            "sharpness_factor": 1.3,
            "threshold": 128
        },
        "photos": {
            "directory": "static/images/photos",
            "max_width": 800,
            "max_height": 440,
            "format": "bmp"
        }
    }
    
    processor = ImageProcessor(config)
    
    # Parse command line arguments
    import argparse
    parser = argparse.ArgumentParser(description="Process images for e-ink display")
    parser.add_argument("input", help="Input image file")
    parser.add_argument("--mode", choices=["bw", "grayscale", "color"], default="grayscale", help="Processing mode")
    parser.add_argument("--nodither", action="store_true", help="Disable dithering")
    parser.add_argument("--filter", choices=["sketch", "edges", "emboss", "posterize"], 
                      help="Apply a specialty filter")
    
    if len(sys.argv) > 1:
        args = parser.parse_args()
        
        if os.path.exists(args.input):
            # Override config settings based on arguments
            if args.mode:
                config["display"]["color_mode"] = args.mode
                
            if args.nodither:
                config["display"]["enable_dithering"] = False
            
            # Re-initialize with updated config
            processor = ImageProcessor(config)
            
            # Process the image
            result_path = processor.preprocess_image(args.input, mode=args.mode)
            
            # Apply specialty filter if requested
            if args.filter and result_path:
                filtered_image = processor.apply_specialty_filter(result_path, args.filter)
                # Save with filter name in filename
                filter_path = result_path.replace(".", f"_{args.filter}.")
                filtered_image.save(filter_path)
                print(f"Filtered image saved to: {filter_path}")
            
            if result_path:
                print(f"Processed image saved to: {result_path}")
            else:
                print("Error processing image")
        else:
            print(f"Image not found: {args.input}")
    else:
        print("Usage: python image_processor.py <input_image> [options]")
        print("Run with --help for more information.")