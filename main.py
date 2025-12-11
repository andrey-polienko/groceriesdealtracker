import os
import requests
from telegram import Bot
import asyncio

# *** 1. CONFIGURATION (MUST CHANGE THESE) ***
# Replace with your actual postal code for local deal finding
POSTAL_CODE = 'M2N 7J6' 

# The list of keywords your script will search for. 
DEALS_OF_INTEREST = [
    # Meat/Protein
    'chicken', 'pork', 'beef', 'steak', 'sausage', 'salmon', 'tuna', 'veal', 'ground', 'turkey', 'lamb',
    # Produce
    'apple', 'pear', 'banana', 'clementine', 'broccoli', 'carrot', 'lettuce', 'cucumbers', 'tomato', 'persimon', 'kiwi',
    # Snacks/Packaged Goods
    'cookie', 'cracker', 'granola', 'chip', 'yogurt', 'cereal', 'ahoy', 'cakester', 'oreo',
    # Dairy
    'lactose free', 'Naturalia', 'gay lee', 'sour cream', 'butter sticks', 'milk', 'purfiltre'
]

# Read secrets from GitHub Actions environment variables (Use the GitHub Secrets setup)
BOT_TOKEN = os.environ.get('TELEGRAM_BOT_TOKEN', 'YOUR_BOT_TOKEN_FOR_LOCAL_TESTING') 
CHAT_ID = os.environ.get('TELEGRAM_CHAT_ID', 'YOUR_CHAT_ID_FOR_LOCAL_TESTING')

# Flipp's base API endpoint
FLIPP_API_URL = f"https://backflipp.wishabi.com/flipp/items/search?locale=en-ca&postal_code={POSTAL_CODE}"


def get_deals():
    """
    Fetches deals by iterating through keywords and compiles a unique list.
    Includes logging to show API response counts for debugging.
    """
    
    # Use a dictionary to store unique items (keys are item IDs)
    all_found_items = {} 
    
    # Iterate through each keyword in your interest list
    for search_keyword in DEALS_OF_INTEREST:
        search_keyword = search_keyword.strip() 
        
        # Construct the URL with the specific keyword
        search_url = f"{FLIPP_API_URL}&q={search_keyword}"
        
        try:
            # 2. GET FLYER DATA for the specific keyword
            print(f"Searching for: {search_keyword}")
            response = requests.get(search_url, timeout=10)
            response.raise_for_status() 
            data = response.json()

            # DEBUG LOGGING
            api_count = len(data.get('items', []))
            print(f"   -> API returned {api_count} items for '{search_keyword}'.")

            # 3. PROCESS AND FILTER DEALS
            for item in data.get('items', []):
                item_id = item.get('id')
                
                # Skip item if already processed
                if item_id in all_found_items:
                    continue 

                store_name = item.
