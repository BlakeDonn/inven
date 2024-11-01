Application Documentation
Overview
This application automates the process of extracting item and trait information from game screenshots and generates a formatted Excel report. It utilizes OCR (Optical Character Recognition) to read text from images, matches the extracted data with known items and traits, and organizes the information in an easy-to-read Excel file.

Features
Image Processing: Crops and preprocesses screenshots to isolate item titles and traits.
OCR Extraction: Uses Tesseract and EasyOCR to extract text from images.
Data Matching: Matches extracted text with known items and traits from CSV files.
Excel Report Generation: Generates a formatted Excel file with conditional formatting and organized data tables.
Workflow
Screenshot Capture: Take screenshots of your game inventory.
Image Cropping: Run the cropping script to split screenshots into title and trait images.
Data Extraction: Use main.py to process cropped images, extract text, and match with known data.
Excel Generation: Use generate_excel.py to create a formatted Excel report from the extracted data.
Usage Instructions
Prerequisites
Python 3.x installed on your system.
Required Python packages:
pytesseract
opencv-python
pandas
openpyxl
easyocr
numpy
rapidfuzz
Installation
Clone the Repository

bash
Copy code
git clone https://github.com/yourusername/yourrepository.git
Navigate to the Project Directory

bash
Copy code
cd yourrepository
Install Python Dependencies

bash
Copy code
pip install -r requirements.txt
Install Tesseract OCR

Windows: Download the installer from here and install it.

Linux: Install via package manager.

bash
Copy code
sudo apt-get install tesseract-ocr
Download Language Data for EasyOCR

EasyOCR should automatically download necessary language data when first run.

Configuration
File Paths

Ensure that the file paths in main.py and generate_excel.py match your directory structure.

Tesseract Path

In main.py, set the path to your Tesseract executable:

python
Copy code
pytesseract.pytesseract.tesseract_cmd = r'C:\Program Files\Tesseract-OCR\tesseract.exe'  # For Windows
Data Files

Place the following CSV files in the project directory:

weapons.csv
armor.csv
accessories.csv
traits.csv
These files should contain the known items and traits for matching.

Running the Application
1. Capture Screenshots
Take clear screenshots of your game inventory, ensuring that item titles and traits are legible.

2. Crop Images
Use the cropping script to split screenshots into title and trait images. Place the cropped images in the cropped_screenshots folder.

3. Extract Data
Run the main data extraction script:

bash
Copy code
python main.py
The script will process the images, extract text using OCR, match items and traits, and save the data to output/processed_inventory.csv.
4. Generate Excel Report
Run the Excel generation script:

bash
Copy code
python generate_excel.py
This will create a formatted Excel file output/processed_inventory.xlsx.
Understanding the Scripts
main.py
Purpose: Processes cropped images, extracts text using OCR, matches items and traits, and saves the data to a CSV file.
Key Functions:
extract_text_from_image: Extracts text from an image using Tesseract and EasyOCR.
find_best_item_match: Matches extracted item names with known items.
find_best_trait_match: Matches extracted trait text with known traits.
process_cropped_images: Processes all images in the cropped_screenshots folder.
generate_excel.py
Purpose: Reads the processed CSV data and generates a formatted Excel report.
Features:
Organizes data into categories (Weapon, Armor, Accessory).
Applies conditional formatting to highlight key metrics.
Formats tables with appropriate fonts, colors, and spacing for readability.