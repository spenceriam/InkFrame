#!/usr/bin/env python3
"""
E-Ink Display Simulator

This module simulates an e-ink display for testing without hardware.
It saves display output to image files for visual inspection.

Usage:
    from src.display.eink_simulator import EInkSimulator
    display = EInkSimulator(display_type="7in5_V2", color_mode="grayscale")
    display.init()
    display.display_image_buffer(image)
"""

import logging
import os
import sys
import time
from datetime import datetime
from pathlib import Path
from typing import Optional, Tuple

from PIL import Image, ImageDraw, ImageFont

logger = logging.getLogger(__name__)


class EInkSimulator:
    """Simulates an e-ink display for testing without hardware"""

    # Display type specifications
    DISPLAY_SPECS = {
        "7in5_V2": {"width": 800, "height": 480, "name": "7.5 inch V2"},
        "7in5_HD": {"width": 880, "height": 528, "name": "7.5 inch HD"},
        "7in5": {"width": 640, "height": 384, "name": "7.5 inch"},
        "7in5b_V2": {"width": 800, "height": 480, "name": "7.5 inch B/W/Red V2"},
        "7in3f": {"width": 800, "height": 480, "name": "7.3 inch ACeP 7-Color"},
    }

    def __init__(self, display_type: str = "7in5_V2", color_mode: str = "grayscale"):
        """
        Initialize the e-ink simulator

        Args:
            display_type: Display model identifier (default: "7in5_V2")
            color_mode: Display mode - "grayscale", "color", or "bw" (default: "grayscale")
        """
        self.display_type = display_type
        self.color_mode = color_mode

        # Get display dimensions from specifications
        specs = self.DISPLAY_SPECS.get(display_type, self.DISPLAY_SPECS["7in5_V2"])
        self.width = specs["width"]
        self.height = specs["height"]
        self.display_name = specs["name"]

        # Determine if this is a color display
        self.is_color_display = color_mode == "color"
        self.grayscale_mode = color_mode == "grayscale"

        # Simulation directory
        self.sim_dir = Path("simulation")
        self.sim_dir.mkdir(parents=True, exist_ok=True)

        # Tracking
        self._initialized = False
        self._display_count = 0
        self._sleep_mode = False

        logger.info(
            f"E-Ink Simulator initialized: {self.display_name} "
            f"({self.width}x{self.height}, mode: {color_mode})"
        )
        logger.info(f"Simulation output directory: {self.sim_dir.absolute()}")

    def init(self) -> bool:
        """
        Initialize the display simulator

        Returns:
            bool: True if successful
        """
        logger.info("Initializing e-ink display simulator...")

        if self._initialized:
            logger.warning("Simulator already initialized")
            return True

        # Create initial display state
        self._current_image = self._create_blank_display()
        self._save_display(self._current_image, "init")

        self._initialized = True
        self._sleep_mode = False
        logger.info("✓ Simulator initialized")
        return True

    def _create_blank_display(self) -> Image.Image:
        """
        Create a blank display image

        Returns:
            PIL.Image: Blank display image
        """
        if self.is_color_display:
            return Image.new("RGB", (self.width, self.height), (255, 255, 255))
        elif self.grayscale_mode:
            return Image.new("L", (self.width, self.height), 255)
        else:
            return Image.new("1", (self.width, self.height), 255)

    def _convert_to_display_mode(self, image: Image.Image) -> Image.Image:
        """
        Convert image to the appropriate display mode

        Args:
            image: PIL Image to convert

        Returns:
            PIL.Image: Converted image
        """
        if self.is_color_display:
            if image.mode != "RGB":
                image = image.convert("RGB")
        elif self.grayscale_mode:
            if image.mode != "L":
                image = image.convert("L")
        else:
            if image.mode != "1":
                image = image.convert("1")

        # Resize to display dimensions if needed
        if image.size != (self.width, self.height):
            image = image.resize((self.width, self.height), Image.Resampling.LANCZOS)

        return image

    def _add_status_info(self, image: Image.Image, filename: str) -> None:
        """
        Add simulation status information to display

        Args:
            image: Image to annotate
            filename: Output filename
        """
        draw = ImageDraw.Draw(image)

        # Add timestamp
        timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        draw.text((10, 10), f"Sim: {timestamp}", fill=0, font=ImageFont.load_default())

        # Add display info
        info = f"{self.display_name} ({self.color_mode})"
        draw.text((10, 30), f"Display: {info}", fill=0, font=ImageFont.load_default())

        # Add refresh count
        refresh_info = f"Refresh #{self._display_count}"
        bbox = draw.textbbox((0, 0), refresh_info, font=ImageFont.load_default())
        text_width = bbox[2] - bbox[0]
        draw.text(
            (self.width - text_width - 10, 10),
            refresh_info,
            fill=0,
            font=ImageFont.load_default(),
        )

    def _save_display(self, image: Image.Image, action: str = "display") -> str:
        """
        Save display state to file

        Args:
            image: Display image to save
            action: Action being performed (for filename)

        Returns:
            str: Path to saved file
        """
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        filename = f"{self.display_name}_{action}_{timestamp}.png"
        filepath = self.sim_dir / filename

        # Add simulation info overlay
        display_copy = image.copy()
        self._add_status_info(display_copy, filename)

        # Save as PNG for easy viewing
        display_copy.save(filepath, "PNG")
        logger.debug(f"Saved simulation output: {filepath}")

        return str(filepath)

    def display_image_buffer(
        self, image: Image.Image, force_refresh: bool = False
    ) -> bool:
        """
        Display an image on the simulated e-ink display

        Args:
            image: PIL Image to display
            force_refresh: Whether to force a full refresh

        Returns:
            bool: True if successful
        """
        if not self._initialized:
            logger.error("Simulator not initialized. Call init() first.")
            return False

        if self._sleep_mode:
            logger.warning("Display is in sleep mode. Wake it first.")
            self._sleep_mode = False

        self._display_count += 1
        refresh_type = "full" if force_refresh else "partial"

        logger.info(
            f"Displaying image (refresh: {refresh_type}, count: {self._display_count})"
        )

        try:
            # Convert image to display mode
            display_image = self._convert_to_display_mode(image)

            # Save to simulation directory
            self._save_display(display_image, f"refresh_{refresh_type}")

            # Update current display state
            self._current_image = display_image

            # Simulate e-ink refresh delay (shorter than real hardware)
            refresh_time = 0.5 if force_refresh else 0.2
            time.sleep(refresh_time)

            return True

        except Exception as e:
            logger.error(f"Error displaying image: {e}")
            return False

    def clear(self) -> bool:
        """
        Clear the e-ink display

        Returns:
            bool: True if successful
        """
        if not self._initialized:
            logger.error("Simulator not initialized. Call init() first.")
            return False

        logger.info("Clearing display")

        try:
            # Create blank display
            blank_image = self._create_blank_display()
            self._save_display(blank_image, "clear")
            self._current_image = blank_image

            return True

        except Exception as e:
            logger.error(f"Error clearing display: {e}")
            return False

    def sleep(self) -> bool:
        """
        Put the e-ink display into sleep mode

        Returns:
            bool: True if successful
        """
        if not self._initialized:
            logger.error("Simulator not initialized. Call init() first.")
            return False

        logger.info("Putting display to sleep")
        self._sleep_mode = True

        # Create a sleep indicator image
        sleep_image = self._current_image.copy()
        draw = ImageDraw.Draw(sleep_image)

        # Add "SLEEP" indicator
        text = "DISPLAY SLEEP"
        font = None
        try:
            font = ImageFont.truetype(
                "/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf", 40
            )
        except:
            font = ImageFont.load_default()

        bbox = draw.textbbox((0, 0), text, font=font)
        text_width = bbox[2] - bbox[0]
        text_height = bbox[3] - bbox[1]

        x = (self.width - text_width) // 2
        y = (self.height - text_height) // 2

        # Draw sleep overlay
        draw.rectangle(
            [(x - 20, y - 10), (x + text_width + 20, y + text_height + 10)],
            fill=255,
            outline=0,
            width=2,
        )
        draw.text((x, y), text, font=font, fill=0)

        self._save_display(sleep_image, "sleep")
        return True

    def close(self) -> None:
        """
        Close the display and release resources

        Returns:
            None
        """
        if not self._initialized:
            logger.warning("Simulator not initialized")
            return

        logger.info("Closing e-ink display simulator")
        self._initialized = False

        # Save final state
        if hasattr(self, "_current_image"):
            self._save_display(self._current_image, "close")

        logger.info("✓ Simulator closed")

    def get_display_info(self) -> dict:
        """
        Get display information

        Returns:
            dict: Display specifications
        """
        return {
            "type": self.display_type,
            "name": self.display_name,
            "width": self.width,
            "height": self.height,
            "color_mode": self.color_mode,
            "is_color": self.is_color_display,
            "is_grayscale": self.grayscale_mode,
            "initialized": self._initialized,
            "sleep_mode": self._sleep_mode,
            "display_count": self._display_count,
        }


def create_simulator(
    display_type: str = "7in5_V2", color_mode: str = "grayscale"
) -> EInkSimulator:
    """
    Factory function to create an e-ink display simulator

    Args:
        display_type: Display model identifier
        color_mode: Display mode

    Returns:
        EInkSimulator: Configured simulator instance
    """
    return EInkSimulator(display_type=display_type, color_mode=color_mode)


if __name__ == "__main__":
    """Test the simulator when run directly"""
    import logging

    logging.basicConfig(
        level=logging.INFO,
        format="%(asctime)s - %(levelname)s - %(message)s",
    )

    logger.info("=== E-Ink Display Simulator Test ===")

    # Create simulator
    display = create_simulator(display_type="7in5_V2", color_mode="grayscale")

    # Initialize
    if not display.init():
        logger.error("Failed to initialize simulator")
        sys.exit(1)

    # Get display info
    info = display.get_display_info()
    logger.info(f"Display Info: {info}")

    # Create and display a test image
    logger.info("\n=== Test 1: Displaying test pattern ===")
    test_image = Image.new("L", (display.width, display.height), 255)
    draw = ImageDraw.Draw(test_image)

    # Draw test pattern
    draw.rectangle([(100, 100), (display.width - 100, display.height - 100)], fill=0)
    draw.text((200, 200), "TEST", font=ImageFont.load_default(), fill=255)

    display.display_image_buffer(test_image, force_refresh=True)

    # Wait a bit
    time.sleep(1)

    # Clear display
    logger.info("\n=== Test 2: Clearing display ===")
    display.clear()

    # Wait a bit
    time.sleep(1)

    # Display another image
    logger.info("\n=== Test 3: Displaying another image ===")
    test_image2 = Image.new("L", (display.width, display.height), 255)
    draw2 = ImageDraw.Draw(test_image2)
    draw2.text((300, 240), "SIMULATOR", font=ImageFont.load_default(), fill=0)

    display.display_image_buffer(test_image2, force_refresh=False)

    # Put to sleep
    logger.info("\n=== Test 4: Putting display to sleep ===")
    time.sleep(1)
    display.sleep()

    # Close
    logger.info("\n=== Test 5: Closing simulator ===")
    display.close()

    logger.info("\n✓ All simulator tests completed!")
    logger.info(f"Check the 'simulation' directory for output images")
