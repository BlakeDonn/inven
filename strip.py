from bs4 import BeautifulSoup
import csv

# Load HTML content from source.html
with open("source.html", "r", encoding="utf-8") as file:
    html_content = file.read()

# Parse the HTML content
soup = BeautifulSoup(html_content, "html.parser")

# Define lists to store weapon, armor, and accessory details
weapons = []
armors = []
accessories = []

# Iterate over each row in the table
for row in soup.find_all("tr"):
    # Initialize variables
    item_name = None
    item_type = None
    item_type_text = None  # New variable to store the item type text
    rarity = None  # New variable for rarity

    # Extract the name and rarity
    name_cell = row.find_all("td", class_="center")
    if name_cell:
        # The first <td> contains the item name with <a> tag
        name_tag = name_cell[0].find("a", class_="a-link")
        if name_tag:
            item_name = name_tag.get_text(strip=True)
        else:
            # If no <a> tag, extract text directly
            item_name = name_cell[0].get_text(strip=True)
        
        # The third <td> contains the rarity
        if len(name_cell) > 2:
            rarity_cell = name_cell[2]
            # Check if rarity is within a <span> with class 'a-red' or directly as text
            span_tag = rarity_cell.find("span", class_="a-red")
            if span_tag:
                rarity_text = span_tag.get_text(strip=True)
                rarity = rarity_text if rarity_text.lower() != "none" else "Unknown"
            else:
                rarity = rarity_cell.get_text(strip=True).strip()

    # Extract the item type from the second <td>
    if name_cell and len(name_cell) > 1:
        item_type_text = name_cell[1].get_text(strip=True)
        # Debug print
        # print(f"Item Name: {item_name}, Item Type Text: {item_type_text}, Rarity: {rarity}")
        # Convert item_type_text to lowercase for case-insensitive comparison
        item_type_text_lower = item_type_text.lower()
        # Classify based on item type keywords
        if any(keyword.lower() in item_type_text_lower for keyword in ["Dagger", "Staff", "Bow", "Sword", "Wand", "Crossbow", "Greatsword"]):
            item_type = "Weapon"
        elif any(keyword.lower() in item_type_text_lower for keyword in ["Armor", "Helmet", "Shield", "Chest", "Boots", "Head", "Legs", "Feet", "Hands", "Cloak", "Gloves", "Pants", "Robes", "Tunic", "Greaves", "Gauntlets", "Plate", "Mail", "Mask", "Vestment", "Hat", "Shoes", "Cap", "Mantle", "Visor", "Circlet", "Hood", "Sabatons"]):
            item_type = "Armor"
        elif any(keyword.lower() in item_type_text_lower for keyword in ["Belt", "Ring", "Bracelet", "Necklace", "Earring", "Amulet", "Pendant", "Charm", "Wristlet", "Bangle", "Collar", "Choker", "Torque"]):
            item_type = "Accessory"

    # Classify and store the item with rarity and type
    if item_name and item_type and item_type_text:
        item_details = {
            "Name": item_name,
            "Type": item_type_text,  # Include the item type text
            "Rarity": rarity
        }
        if item_type == "Weapon":
            weapons.append(item_details)
        elif item_type == "Armor":
            armors.append(item_details)
        elif item_type == "Accessory":
            accessories.append(item_details)

# Function to save items to CSV
def save_items_to_csv(items, file_name, item_type):
    with open(file_name, "w", newline='', encoding="utf-8") as file:
        writer = csv.writer(file)
        header = [f"{item_type} Name", "Type", "Rarity"]
        writer.writerow(header)
        for item in items:
            writer.writerow([item["Name"], item["Type"], item["Rarity"]])

# Save weapons to weapons.csv
save_items_to_csv(weapons, "weapons.csv", "Weapon")

# Save armors to armor.csv
save_items_to_csv(armors, "armor.csv", "Armor")

# Save accessories to accessories.csv
save_items_to_csv(accessories, "accessories.csv", "Accessory")

print("Extraction complete. Data saved to weapons.csv, armor.csv, and accessories.csv.")
