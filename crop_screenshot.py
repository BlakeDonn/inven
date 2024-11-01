import os
import cv2
from PIL import Image
import logging
from datetime import datetime

# Paths
SCREENSHOT_FOLDER = 'screenshots'            # Folder containing screenshots
TEMPLATES_FOLDER = 'templates'               # Folder containing template images (structural templates)
CROPPED_FOLDER = 'cropped_screenshots'       # Folder to save cropped images
LOG_FILE = 'crop_screenshot.log'             # Log file path

# Logging setup
logging.basicConfig(level=logging.INFO, format='%(asctime)s [%(levelname)s] %(message)s', handlers=[logging.FileHandler(LOG_FILE), logging.StreamHandler()])

def load_template(template_path):
    """
    Load a single template for structure-based matching.
    """
    template = cv2.imread(template_path, cv2.IMREAD_GRAYSCALE)
    if template is None:
        logging.error(f"Failed to load template image from '{template_path}'.")
    return template

def crop_sections(screenshot_path, title_template, trait_template, output_folder):
    """
    Crop item title and trait sections based on structural templates and fixed offsets.
    """
    try:
        # Load the screenshot
        screenshot = cv2.imread(screenshot_path)
        if screenshot is None:
            logging.error(f"Failed to load screenshot '{screenshot_path}'.")
            return
        
        screenshot_gray = cv2.cvtColor(screenshot, cv2.COLOR_BGR2GRAY)
        
        # Define offsets to expand the cropped area from the matched region
        TITLE_EXPAND_WIDTH = 400  # Adjust width as needed
        TITLE_EXPAND_HEIGHT = 75 # Adjust height as needed
        TRAIT_EXPAND_WIDTH = 400  # Adjust width as needed
        TRAIT_EXPAND_HEIGHT = 75 # Adjust height as needed

        # Perform template matching for title region
        res_title = cv2.matchTemplate(screenshot_gray, title_template, cv2.TM_CCOEFF_NORMED)
        _, max_val_title, _, max_loc_title = cv2.minMaxLoc(res_title)
        
        # Perform template matching for trait region
        res_trait = cv2.matchTemplate(screenshot_gray, trait_template, cv2.TM_CCOEFF_NORMED)
        _, max_val_trait, _, max_loc_trait = cv2.minMaxLoc(res_trait)
        
        # Get a unique timestamp with milliseconds for each image
        timestamp = datetime.now().strftime('%Y%m%d_%H%M%S_%f')  # includes microseconds
        
        # Crop Title Section
        x, y = max_loc_title
        title_crop = screenshot[y:y+TITLE_EXPAND_HEIGHT, x:x+TITLE_EXPAND_WIDTH]
        title_image_path = os.path.join(output_folder, f"title_cropped_{timestamp}.png")
        Image.fromarray(cv2.cvtColor(title_crop, cv2.COLOR_BGR2RGB)).save(title_image_path)
        logging.info(f"Cropped title image saved at '{title_image_path}'")
        
        # Crop Trait Section
        x, y = max_loc_trait
        trait_crop = screenshot[y:y+TRAIT_EXPAND_HEIGHT, x:x+TRAIT_EXPAND_WIDTH]
        trait_image_path = os.path.join(output_folder, f"trait_cropped_{timestamp}.png")
        Image.fromarray(cv2.cvtColor(trait_crop, cv2.COLOR_BGR2RGB)).save(trait_image_path)
        logging.info(f"Cropped trait image saved at '{trait_image_path}'")
        
    except Exception as e:
        logging.error(f"Error cropping sections from '{screenshot_path}': {e}")

def main():
    os.makedirs(CROPPED_FOLDER, exist_ok=True)
    
    # Load structural templates for title and trait regions
    title_template_path = os.path.join(TEMPLATES_FOLDER, 'title_template.png')
    trait_template_path = os.path.join(TEMPLATES_FOLDER, 'trait_template.png')
    title_template = load_template(title_template_path)
    trait_template = load_template(trait_template_path)
    
    if title_template is None or trait_template is None:
        logging.error("Failed to load one or more templates. Exiting.")
        return
    
    # Process all screenshots in the folder
    for screenshot_file in os.listdir(SCREENSHOT_FOLDER):
        screenshot_path = os.path.join(SCREENSHOT_FOLDER, screenshot_file)
        if screenshot_file.lower().endswith(('.png', '.jpg', '.jpeg')):
            crop_sections(screenshot_path, title_template, trait_template, CROPPED_FOLDER)

if __name__ == "__main__":
    main()
