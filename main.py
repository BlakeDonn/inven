import os
import pytesseract
from PIL import Image
import cv2
import csv
import logging
import re
import pandas as pd
from rapidfuzz import process, fuzz
import numpy as np
import easyocr
from concurrent.futures import ThreadPoolExecutor

# ------------------- Configuration -------------------

# Path to Tesseract executable
pytesseract.pytesseract.tesseract_cmd = r'C:\Program Files\Tesseract-OCR\tesseract.exe'  # For Windows

# Number of threads for parallel processing
MAX_WORKERS = 4

# File paths
WEAPONS_CSV = "weapons.csv"
ARMOR_CSV = "armor.csv"
ACCESSORIES_CSV = "accessories.csv"  # New line for accessories
TRAITS_CSV = "traits.csv"
CROPPED_FOLDER = 'cropped_screenshots/'
OUTPUT_FOLDER = 'output/'
OUTPUT_CSV = os.path.join(OUTPUT_FOLDER, 'processed_inventory.csv')
LOG_FILE = "app.log"

# -----------------------------------------------------

# ------------------- Logging Setup -------------------
logging.basicConfig(
    level=logging.DEBUG,
    format='%(asctime)s [%(levelname)s] %(message)s',
    handlers=[
        logging.FileHandler(LOG_FILE),
        logging.StreamHandler()
    ]
)
# -----------------------------------------------------

# ------------------- OCR Engine Setup -------------------
easy_reader = easyocr.Reader(['en'])  # Initialize EasyOCR with English
# ---------------------------------------------------------


# ------------------- Text Normalization -------------------
def normalize_text(text):
    # Minimal normalization to preserve item names
    text = text.strip()
    return text
# ---------------------------------------------------------


def load_items_with_rarity(file_path):
    items = {}
    normalized_items = {}
    try:
        with open(file_path, "r", encoding="utf-8") as file:
            reader = csv.reader(file)
            header = next(reader)  # Read the header row
            name_index = 0  # Default index for item name
            type_index = 1  # Default index for item type
            rarity_index = 2  # Default index for rarity

            # Adjust indices based on header names
            if "Weapon Name" in header:
                name_index = header.index("Weapon Name")
            elif "Armor Name" in header:
                name_index = header.index("Armor Name")
            elif "Accessory Name" in header:
                name_index = header.index("Accessory Name")
            if "Type" in header:
                type_index = header.index("Type")
            if "Rarity" in header:
                rarity_index = header.index("Rarity")

            for row in reader:
                if len(row) > max(name_index, type_index, rarity_index):
                    item_name = row[name_index].strip()
                    item_type = row[type_index].strip()
                    rarity = row[rarity_index].strip()
                    items[item_name] = {
                        'Type': item_type,
                        'Rarity': rarity
                    }
                    normalized_name = normalize_text(item_name).lower()
                    normalized_items[normalized_name] = item_name
        logging.info(f"Loaded {len(items)} items from {file_path}")
    except Exception as e:
        logging.error(f"Error loading items from {file_path}: {e}")
    return items, normalized_items


def load_traits(file_path):
    traits = []
    normalized_traits = []
    try:
        with open(file_path, "r", encoding="utf-8") as file:
            reader = csv.reader(file)
            next(reader)  # Skip header
            for row in reader:
                if row:
                    trait = row[0].strip()
                    traits.append(trait)
                    normalized_trait = normalize_text(trait).lower()
                    normalized_traits.append(normalized_trait)
        logging.info(f"Loaded {len(traits)} traits from {file_path}")
    except Exception as e:
        logging.error(f"Error loading traits from {file_path}: {e}")
    return traits, normalized_traits
# ------------------------------------------------------------


# ------------------- Load Data -------------------
weapons_items, weapons_normalized = load_items_with_rarity(WEAPONS_CSV)
armor_items, armor_normalized = load_items_with_rarity(ARMOR_CSV)
accessories_items, accessories_normalized = load_items_with_rarity(ACCESSORIES_CSV)  # Load accessories
known_items = {**weapons_items, **armor_items, **accessories_items}
normalized_items = {**weapons_normalized, **armor_normalized, **accessories_normalized}
traits, normalized_traits = load_traits(TRAITS_CSV)
normalized_traits_set = set(normalized_traits)

# Create a list of all possible item names for matching
item_names = list(known_items.keys())
normalized_item_names = list(normalized_items.keys())
# -----------------------------------------------------


# ------------------- OCR Text Cleaning -------------------
def clean_ocr_text(text):
    # Basic corrections
    text = text.replace('\n', ' ').strip()
    return text
# -------------------------------------------------------


# ------------------- Image Preprocessing -------------------
def preprocess_image(img):
    try:
        gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
    except Exception as e:
        logging.error(f"Error converting image to grayscale: {e}")
        return None

    # Resize image to improve OCR accuracy
    gray = cv2.resize(gray, None, fx=2, fy=2, interpolation=cv2.INTER_LINEAR)

    # Apply Gaussian blur to reduce noise
    gray = cv2.GaussianBlur(gray, (3, 3), 0)

    # Apply thresholding
    _, thresh = cv2.threshold(gray, 0, 255, cv2.THRESH_BINARY + cv2.THRESH_OTSU)

    return thresh
# ---------------------------------------------------------


# ------------------- OCR Extraction -------------------
def extract_text_with_tesseract(image, image_type='title'):
    processed_img = preprocess_image(image)
    if processed_img is None:
        return "", 0
    pil_img = Image.fromarray(processed_img)
    config = '--psm 7 -l eng' if image_type == 'title' else '--psm 6 -l eng'
    try:
        data = pytesseract.image_to_data(pil_img, config=config, output_type=pytesseract.Output.DICT)
        text = " ".join([word for word in data['text'] if word.strip() != ""])
        conf_list = [int(c) for c in data['conf'] if str(c).isdigit() and int(c) > 0]
        if conf_list:
            conf = np.mean(conf_list)  # Average confidence
        else:
            conf = 0
        text = clean_ocr_text(text)
        logging.debug(f"Tesseract OCR text ({image_type}): '{text}' with confidence {conf}")
        return text.strip(), conf
    except Exception as e:
        logging.error(f"Tesseract OCR failed for {image_type}: {e}")
        return "", 0


def extract_text_with_easyocr_func(image, image_type='title'):
    processed_img = preprocess_image(image)
    if processed_img is None:
        return "", 0
    try:
        # EasyOCR expects RGB images
        rgb_img = cv2.cvtColor(processed_img, cv2.COLOR_GRAY2RGB)
        result = easy_reader.readtext(rgb_img)
        text = " ".join([res[1] for res in result])
        conf = np.mean([res[2] for res in result]) if result else 0
        text = clean_ocr_text(text)
        logging.debug(f"EasyOCR text ({image_type}): '{text}' with confidence {conf}")
        return text.strip(), conf
    except Exception as e:
        logging.error(f"EasyOCR failed for {image_type}: {e}")
        return "", 0


def extract_text_from_image(image, image_type='title'):
    # Use both OCR engines and choose the result with higher confidence
    tesseract_text, tesseract_conf = extract_text_with_tesseract(image, image_type)
    easyocr_text, easyocr_conf = extract_text_with_easyocr_func(image, image_type)

    if tesseract_conf >= easyocr_conf:
        final_text = tesseract_text
    else:
        final_text = easyocr_text

    logging.debug(f"Final OCR text ({image_type}): '{final_text}' with Tesseract conf: {tesseract_conf}, EasyOCR conf: {easyocr_conf}")
    return final_text
# ----------------------------------------------------------


# ------------------- Trait Text Processing -------------------
def process_trait_text(trait_text):
    # Remove 'Trait' and any non-alphanumeric characters
    cleaned_text = re.sub(r'[^a-zA-Z0-9\s]', '', trait_text)
    # Remove the word 'Trait' and any numbers
    cleaned_text = re.sub(r'\bTrait\b', '', cleaned_text, flags=re.IGNORECASE)
    cleaned_text = re.sub(r'\d+', '', cleaned_text)
    # Remove extra whitespace and convert to lowercase
    cleaned_text = cleaned_text.strip().lower()
    logging.debug(f"Processed trait text: '{cleaned_text}'")
    return cleaned_text
# ------------------------------------------------------------


# ------------------- Matching Functions -------------------
def find_best_item_match(ocr_text):
    normalized_text = ocr_text.lower()
    # Exact match
    if normalized_text in normalized_items:
        matched_name = normalized_items[normalized_text]
        item_info = known_items[matched_name]
        logging.debug(f"Exact matched '{ocr_text}' to '{matched_name}'")
        return matched_name, item_info

    # Fuzzy matching
    matches = process.extract(
        normalized_text, normalized_item_names,
        scorer=fuzz.token_sort_ratio, limit=5
    )
    # Filter matches with score >= 80
    high_score_matches = [match for match in matches if match[1] >= 80]
    if high_score_matches:
        # Sort by score (descending) and length (descending)
        high_score_matches.sort(key=lambda x: (x[1], len(x[0])), reverse=True)
        best_match = high_score_matches[0]
        matched_normalized_name = best_match[0]
        matched_name = normalized_items[matched_normalized_name]
        item_info = known_items[matched_name]
        logging.debug(f"Fuzzy matched '{ocr_text}' to '{matched_name}' with score {best_match[1]}")
        return matched_name, item_info
    else:
        logging.warning(f"Unmatched item: '{ocr_text}'")
        return None, None


def find_best_trait_match(normalized_text):
    # Exact match
    if normalized_text in normalized_traits_set:
        index = normalized_traits.index(normalized_text)
        trait_name = traits[index]
        logging.debug(f"Exact matched trait '{normalized_text}' to '{trait_name}'")
        return trait_name

    # Fuzzy matching
    matches = process.extract(
        normalized_text, normalized_traits,
        scorer=fuzz.token_sort_ratio, limit=5
    )
    # Filter matches with score >= 80
    high_score_matches = [match for match in matches if match[1] >= 80]
    if high_score_matches:
        # Sort by score (descending) and length (descending)
        high_score_matches.sort(key=lambda x: (x[1], len(x[0])), reverse=True)
        best_match = high_score_matches[0]
        matched_normalized_trait = best_match[0]
        index = normalized_traits.index(matched_normalized_trait)
        trait_name = traits[index]
        logging.debug(f"Fuzzy matched trait '{normalized_text}' to '{trait_name}' with score {best_match[1]}")
        return trait_name
    else:
        logging.warning(f"Unmatched trait: '{normalized_text}'")
        return None
# ----------------------------------------------------------


# ------------------- Process Single Image Group -------------------
def process_single_image_group(unique_id, paths):
    title_path = paths.get('title')
    trait_path = paths.get('trait')
    matched_items, matched_traits = [], []
    rarity = "Unknown"
    item_type = "Unknown"

    if title_path and trait_path:
        # Process title image
        title_img = cv2.imread(title_path)
        if title_img is not None:
            title_text = extract_text_from_image(title_img, 'title')
            logging.debug(f"Unique ID {unique_id}: OCR title text: '{title_text}'")

            # Find best item match
            item_name, item_info = find_best_item_match(title_text)
            if item_name:
                matched_items.append(item_name)
                rarity = item_info['Rarity']
                item_type = item_info['Type']
                logging.debug(f"Unique ID {unique_id}: Matched item '{item_name}' with rarity '{rarity}' and type '{item_type}'")
            else:
                matched_items.append("No Match Found")
                logging.debug(f"Unique ID {unique_id}: No item match found.")

        # Process trait image
        trait_img = cv2.imread(trait_path)
        if trait_img is not None:
            trait_text = extract_text_from_image(trait_img, 'trait')
            logging.debug(f"Unique ID {unique_id}: OCR trait text: '{trait_text}'")

            # Clean and normalize the trait text
            normalized_trait_text = process_trait_text(trait_text)

            # Find best trait match
            trait_name = find_best_trait_match(normalized_trait_text)
            if trait_name:
                matched_traits.append(trait_name)
                logging.debug(f"Unique ID {unique_id}: Matched trait '{trait_name}'")
            else:
                matched_traits.append("No Traits Found")
                logging.debug(f"Unique ID {unique_id}: No trait match found.")

        # Save the processed data for the current pair
        item_info = {
            "File": unique_id,
            "Matched Items": ', '.join(matched_items),
            "Type": item_type,
            "Rarity": rarity,
            "Matched Traits": ', '.join(matched_traits)
        }
        return item_info
    else:
        logging.warning(f"Unique ID {unique_id}: Missing title or trait image.")
        return None

# --------------------------------------------------------------


# ------------------- Process Cropped Images -------------------
def process_cropped_images():
    data = []
    if not os.path.exists(CROPPED_FOLDER):
        logging.error(f"Cropped folder does not exist: {CROPPED_FOLDER}")
        return data

    files = sorted(os.listdir(CROPPED_FOLDER))
    image_groups = {}

    # Group images by unique identifier
    for file in files:
        unique_id = re.search(r'_(\d+)\.png$', file)
        if unique_id:
            unique_id = unique_id.group(1)
            if unique_id not in image_groups:
                image_groups[unique_id] = {}
            if file.startswith("title_cropped"):
                image_groups[unique_id]['title'] = os.path.join(CROPPED_FOLDER, file)
            elif file.startswith("trait_cropped"):
                image_groups[unique_id]['trait'] = os.path.join(CROPPED_FOLDER, file)

    logging.info(f"Found {len(image_groups)} unique image groups.")

    # Process images in parallel
    with ThreadPoolExecutor(max_workers=MAX_WORKERS) as executor:
        futures = [executor.submit(process_single_image_group, uid, paths)
                   for uid, paths in image_groups.items()]
        for future in futures:
            result = future.result()
            if result:
                data.append(result)

    logging.info(f"Total items processed: {len(data)}")
    return data
# --------------------------------------------------------------


# ------------------- Save Data to CSV -------------------
def save_data(data):
    if not data:
        logging.warning("No data to save.")
        return
    os.makedirs(OUTPUT_FOLDER, exist_ok=True)
    df = pd.DataFrame(data)
    try:
        df.to_csv(OUTPUT_CSV, index=False)
        logging.info(f"Data successfully saved to {OUTPUT_CSV}")
    except Exception as e:
        logging.error(f"Failed to save data to CSV: {e}")

# ---------------------------------------------------------


# ------------------- Main Execution -------------------
if __name__ == '__main__':
    logging.info("Starting OCR Extraction Process")
    data = process_cropped_images()
    save_data(data)
    logging.info("Data extraction complete. Processed data saved to 'output/processed_inventory.csv'.")
# -------------------------------------------------------
