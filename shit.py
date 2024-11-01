import csv

# List of traits
traits = [
    "Melee Evasion", "Melee Endurance", "Ranged Evasion", "Ranged Endurance", 
    "Max Health", "Health Regen", "Max Mana", "Mana Regen", "Cooldown Speed", 
    "Buff Duration", "Attack Speed", "Debuff Duration", "Movement Speed", 
    "Magic Evasion", "Magic Endurance", "Skill Damage Resistance", 
    "Weaken Resistance", "Sleep Resistance", "Collision Resistance", 
    "Silence Resistance", "Fear Resistance", "Petrification Resistance", 
    "Stun Resistance", "Skill Damage Boost", "Collision Chance", "Silence Chance", 
    "Weaken Chance", "Sleep Chance", "Fear Chance", "Petrification Chance", 
    "Stun Chance", "Ranged Hit Chance", "Ranged Critical Hit Chance", 
    "Ranged Heavy Attack Chance", "Wildkin Bonus Damage", "Insectum Bonus Damage", 
    "Plantaria Bonus Damage", "Construct Bonus Damage", "Undead Bonus Damage", 
    "Einarden Bonus Damage", "Spiritus Bonus Damage", "Mana Cost Efficiency", 
    "Demon Bonus Damage", "Melee Hit Chance", "Melee Critical Hit Chance", 
    "Melee Heavy Attack Chance", "Magic Hit Chance", "Magic Critical Hit Chance", 
    "Magic Heavy Attack Chance", "Bind Resistance", "Bind Chance", "Hit Chance", 
    "Critical Hit Chance", "Heavy Attack Chance", "Max Stamina", 
    "Attack Range Increase", "Attack Speed", "Off-Hand Double Attack Chance", 
    "Base Damage", "Movement Speed", "Range", "Melee Defense", "Ranged Defense", 
    "Magic Defense", "Shield Block Chance", "Strength", "Dexterity", "Wisdom", 
    "Perception", "Bonus Damage", "Damage Reduction", "Melee Heavy Attack Evasion", 
    "Ranged Heavy Attack Evasion", "Magic Heavy Attack Evasion", "Potion Healing", 
    "Amitoi Healing", "Stamina Regen", "Humanoid Bonus Damage", "Draconus Bonus Damage", 
    "Humanoid Damage Reduction", "Einarden Damage Reduction", "Draconus Damage Reduction", 
    "Demon Damage Reduction", "Undead Damage Reduction", "Construct Damage Reduction", 
    "Spiritus Damage Reduction", "Wildkin Damage Reduction", "Insectum Damage Reduction", 
    "Plantaria Damage Reduction", "Aura Effect", "Aura Range", "Recovery Effect", 
    "Healing", "Healing Received", "Aggro", "EXP Bonus", "Item Chance", 
    "Sollant Bonus", "Crafting Material Chance", "Stun Immunity", 
    "Petrification Immunity", "Sleep Immunity", "Silence Immunity", 
    "Bind Immunity", "Fear Immunity", "Collision Immunity", "Global Cooldown Speed", 
    "Abyssal Contract Token Bonus", "Abyssal Contract Token Efficiency", 
    "Mastery Bonus", "Shield Damage Reduction", "PvP Melee Critical Hit Chance", 
    "PvP Ranged Critical Hit Chance", "PvP Magic Critical Hit Chance", 
    "PvP Melee Endurance", "PvP Ranged Endurance", "PvP Magic Endurance", 
    "PvP Melee Hit Chance", "PvP Ranged Hit Chance", "PvP Magic Hit Chance", 
    "PvP Melee Evasion", "PvP Ranged Evasion", "PvP Magic Evasion", 
    "PvP Melee Heavy Attack Chance", "PvP Ranged Heavy Attack Chance", 
    "PvP Magic Heavy Attack Chance", "PvP Melee Heavy Attack Evasion", 
    "PvP Ranged Heavy Attack Evasion", "PvP Magic Heavy Attack Evasion", 
    "PvP Critical Weaken Chance", "PvP Critical Stun Chance", 
    "PvP Critical Petrification Chance", "PvP Critical Sleep Chance", 
    "PvP Critical Silence Chance", "PvP Critical Fear Chance", "PvP Critical Bind Chance", 
    "PvP Weaken Endurance", "PvP Stun Endurance", "PvP Petrification Endurance", 
    "PvP Sleep Endurance", "PvP Silence Endurance", "PvP Fear Endurance", 
    "PvP Bind Endurance", "PvP Double Weaken", "PvP Double Stun", 
    "PvP Double Petrification", "PvP Double Sleep", "PvP Double Silence", 
    "PvP Double Fear", "PvP Double Bind", "PvP Double Weaken Evasion", 
    "PvP Double Stun Evasion", "PvP Double Petrification Evasion", 
    "PvP Double Sleep Evasion", "PvP Double Silence Evasion", "PvP Double Fear Evasion", 
    "PvP Double Bind Evasion", "Boss Bonus Damage", "Boss Damage Reduction", 
    "Boss Melee Critical Hit Chance", "Boss Ranged Critical Hit Chance", 
    "Boss Magic Critical Hit Chance", "Boss Melee Endurance", "Boss Ranged Endurance", 
    "Boss Magic Endurance", "Boss Melee Hit Chance", "Boss Ranged Hit Chance", 
    "Boss Magic Hit Chance", "Boss Melee Evasion", "Boss Ranged Evasion", 
    "Boss Magic Evasion", "Boss Melee Heavy Attack Chance", 
    "Boss Ranged Heavy Attack Chance", "Boss Magic Heavy Attack Chance", 
    "Boss Melee Heavy Attack Evasion", "Boss Ranged Heavy Attack Evasion", 
    "Boss Magic Heavy Attack Evasion", "Gathering Speed", "Double Gathering", 
    "Special Item Chance", "Summon Duration", "All Evasion", "Dash Morph Accel. Bonus", 
    "Dash Morph Speed Bonus", "Aqua. Morph Accel. Bonus", "Aqua. Morph Speed Bonus", 
    "Glide Morph Accel. Bonus", "Glide Morph Speed Bonus", "Stamina Cost Efficiency", 
    "Defense", "Evasion", "Endurance", "Heavy Attack Evasion", "Boss Hit Chance", 
    "Boss Critical Hit Chance", "Boss Heavy Attack Chance", "Boss Evasion", 
    "Boss Endurance", "Boss Heavy Attack Evasion", "PvP Hit Chance", 
    "PvP Critical Hit Chance", "PvP Heavy Attack Chance", "PvP Evasion", 
    "PvP Endurance", "PvP Heavy Attack Evasion", "CC Chance", "CC Resistances", 
    "Shield Block Penetration Chance", "Critical Damage", "Critical Damage Reduction", 
    "Humanoid Damage Boost", "Undead Damage Boost", "Wildkin Damage Boost", 
    "Construct Damage Boost", "Demon Damage Boost", "Humanoid Damage Resistance", 
    "Undead Damage Resistance", "Wildkin Damage Resistance", "Construct Damage Resistance", 
    "Demon Damage Resistance", "Fishing EXP", "Large Fish Bite Chance", 
    "Medium Fish Bite Chance", "Small Fish Bite Chance", "Fishing Bonus Level", 
    "Cooking EXP", "PvP Damage", "PvP Damage Taken"
]

# Write traits to CSV file
with open("traits.csv", "w", newline='', encoding="utf-8") as file:
    writer = csv.writer(file)
    writer.writerow(["Trait"])  # Header
    for trait in traits:
        writer.writerow([trait])

print("Traits CSV file created as 'traits.csv'.")