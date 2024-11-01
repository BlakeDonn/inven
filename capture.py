import os
import time
import datetime
import logging
import pyautogui
import keyboard
from PIL import ImageFont, ImageDraw, Image
from threading import Thread

# ----------------------- Configuration -----------------------

# Hotkey combination to trigger screenshot (e.g., 'ctrl+shift+s')
HOTKEY = 'ctrl+shift+s'

BASE_CAPTURE_WIDTH = 600  # Wider to accommodate larger item boxes
BASE_CAPTURE_HEIGHT = 1000  # Taller for full item descriptions

# Offset from the cursor position (left, top)
OFFSET_LEFT = -600  # Shift left to better center on item box
OFFSET_TOP = -100   # Adjust top offset to align with item box height

# Folder to save screenshots
SCREENSHOT_FOLDER = 'screenshots'

# Log file path
LOG_FILE = 'screenshot_automation.log'

# Font for measuring text size (adjust path if needed)
FONT_PATH = "/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf"
FONT_SIZE = 16

# ------------------------------------------------------------

def setup_logging():
    """
    Configure logging to file and console.
    """
    logging.basicConfig(
        level=logging.INFO,
        format='%(asctime)s [%(levelname)s] %(message)s',
        handlers=[
            logging.FileHandler(LOG_FILE),
            logging.StreamHandler()
        ]
    )
    logging.info("Logging is set up.")

def create_screenshot_folder():
    """
    Create the screenshot folder if it doesn't exist.
    """
    if not os.path.exists(SCREENSHOT_FOLDER):
        os.makedirs(SCREENSHOT_FOLDER)
        logging.info(f"Created screenshot folder at '{SCREENSHOT_FOLDER}'.")
    else:
        logging.info(f"Screenshots will be saved to '{SCREENSHOT_FOLDER}'.")

def calculate_dynamic_capture_size(text="Example Item Name", traits=[]):
    """
    Calculate capture width and height based on the longest text input.
    """
    try:
        font = ImageFont.truetype(FONT_PATH, FONT_SIZE)
        max_text_width = max(font.getsize(text)[0], *(font.getsize(trait)[0] for trait in traits))
        
        dynamic_width = max(BASE_CAPTURE_WIDTH, max_text_width + 100)  # add some padding
        dynamic_height = max(BASE_CAPTURE_HEIGHT, 200 + 20 * len(traits))  # base height + trait lines

        logging.info(f"Calculated dynamic size: Width={dynamic_width}, Height={dynamic_height}")
        return dynamic_width, dynamic_height
    except Exception as e:
        logging.error(f"Failed to calculate dynamic size: {e}")
        return BASE_CAPTURE_WIDTH, BASE_CAPTURE_HEIGHT

def capture_screenshot():
    """
    Capture a screenshot of a region slightly to the left of the mouse cursor and save it.
    """
    try:
        # Dummy text for testing dynamic size calculation
        item_name = "Lequirus's Wicked Thorns"
        traits = ["Humanoid Bonus Damage", "Off-Hand Double Attack"]

        # Get current mouse position
        x, y = pyautogui.position()
        logging.info(f"Mouse position: ({x}, {y})")

        # Calculate dynamic capture size
        capture_width, capture_height = calculate_dynamic_capture_size(item_name, traits)

        # Calculate the top-left corner of the capture area with offset
        left = x + OFFSET_LEFT
        top = y + OFFSET_TOP

        # Ensure the capture area is within screen bounds
        screen_width, screen_height = pyautogui.size()
        left = max(0, min(left, screen_width - capture_width))
        top = max(0, min(top, screen_height - capture_height))

        logging.info(f"Capturing region: Left={left}, Top={top}, Width={capture_width}, Height={capture_height}")

        # Capture the region
        screenshot = pyautogui.screenshot(region=(left, top, capture_width, capture_height))

        # Generate timestamped filename
        timestamp = datetime.datetime.now().strftime('%Y%m%d_%H%M%S')
        filename = f"screenshot_{timestamp}.png"
        filepath = os.path.join(SCREENSHOT_FOLDER, filename)

        # Save the screenshot
        screenshot.save(filepath)
        logging.info(f"Screenshot saved as '{filepath}'.")

    except Exception as e:
        logging.error(f"Failed to capture screenshot: {e}")

def hotkey_listener():
    """
    Listen for the hotkey and capture screenshot when triggered.
    """
    logging.info(f"Listening for hotkey '{HOTKEY}' to capture screenshots.")
    keyboard.add_hotkey(HOTKEY, capture_screenshot)
    # Block forever, waiting for hotkeys
    keyboard.wait()

def main():
    setup_logging()
    create_screenshot_folder()

    # Start the hotkey listener in a separate thread
    listener_thread = Thread(target=hotkey_listener, daemon=True)
    listener_thread.start()

    logging.info("Screenshot automation is running. Press ESC to exit.")

    try:
        while True:
            time.sleep(1)
    except KeyboardInterrupt:
        logging.info("Screenshot automation terminated by user.")

if __name__ == "__main__":
    main()
