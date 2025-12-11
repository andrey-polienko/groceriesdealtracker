import os
import requests
from telegram import Bot
import asyncio

# *** 1. CONFIGURATION (MUST CHANGE THESE) ***

# Replace with your actual postal code for local deal finding
POSTAL_CODE = 'M2N 7J6' 

# List of preferred merchants (case-insensitive check will be used)
PREFERRED_STORES = [
    'Food Basics',
    'No Frills',
    'Loblaws',
    'T&T Supermarket',
    "Longo's",
    'Walmart'
]

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

# Telegram's limit is 4096 characters. We use 3500 to leave a buffer for Markdown and headers.
TELEGRAM_MESSAGE_LIMIT = 3500

# Read secrets from GitHub Actions environment variables (Use the GitHub Secrets setup)
BOT_TOKEN = os.environ.get('TELEGRAM_BOT_TOKEN', 'YOUR_BOT_TOKEN_FOR_LOCAL_TESTING') 
CHAT_ID = os.environ.get('TELEGRAM_CHAT_ID', 'YOUR_CHAT_ID_FOR_LOCAL_TESTING')

# Flipp's base API endpoint
FLIPP_API_URL = f"https://backflipp.wishabi.com/flipp/items/search?locale=en-ca&postal_code={POSTAL_CODE}"


def get_deals():
    """
    Fetches deals by iterating through keywords, filters by PREFERRED_STORES, 
    and compiles a unique list.
    """
    
    # Use a dictionary to store unique items (keys are item IDs)
    all_found_items = {} 
    
    # Create a list of preferred store names in lower case for easy comparison
    lower_preferred_stores = [name.lower() for name in PREFERRED_STORES]
    
    # Iterate through each keyword in your interest list
    for search_keyword in DEALS_OF_INTEREST:
        search_keyword = search_keyword.strip() 
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

                store_name = item.get('merchant_name', 'Unknown Store')
                
                # *** FILTER 1: Store Name Filter ***
                if store_name.lower() not in lower_preferred_stores:
                    continue # Skip this deal if the store is not on our list
                # ***********************************
                
                # FIX: Defensive coding against NoneType error (Handles null values from API)
                item_name = str(item.get('flyer_item_description') or '').lower()
                product_name = str(item.get('name') or '').lower()
                
                # *** FILTER 2: Keyword Match Filter ***
                is_match = False
                if search_keyword.lower() in item_name or search_keyword.lower() in product_name:
                    is_match = True
                
                if is_match:
                    price = item.get('current_price', 'Price Not Listed')
                    discount = item.get('pre_price_text', '') 

                    all_found_items[item_id] = {
                        'product': item.get('name', 'N/A'),
                        'store': store_name,
                        'price': price,
                        'discount': discount,
                        'description': item_name
                    }
            
            print(f"   -> Total unique deals found so far: {len(all_found_items)}")


        except requests.exceptions.RequestException as e:
            print(f"Error fetching data for {search_keyword}: {e}")
            
    return list(all_found_items.values())


async def send_notification(deals):
    """Formats the deals list and sends it via Telegram, using pagination for long lists."""
    
    if not deals:
        message = "No new deals found for your interests this week!"
        messages_to_send = [message]
    else:
        # Group all deals by store
        stores = {}
        for deal in deals:
            store = deal['store']
            if store not in stores:
                stores[store] = []
            stores[store].append(deal)

        # --- Build Message Pages ---
        messages_to_send = []
        current_message = "" 
        
        # Iterate through stores and build the message page by page
        for store, store_deals in stores.items():
            store_header = f"--- 🏢 **{store}** ({len(store_deals)} deals) ---\n"
            
            # If the current page is empty, start it with the primary header
            if not current_message.strip():
                 current_message = "🛒 **Weekly Grocery Deals Alert!** 🛒\n\n"
                 current_message += f"**Total Deals Found:** {len(deals)}\n"
                 current_message += "\n"

            # Check if adding the new store header will cause an overflow
            if len(current_message) + len(store_header) > TELEGRAM_MESSAGE_LIMIT:
                # Finalize the current message and start a new page
                current_message += "\n(Message too long, continued below...)"
                messages_to_send.append(current_message)
                current_message = f"🛒 **Weekly Grocery Deals Alert! (Cont.)** 🛒\n\n"
            
            current_message += store_header

            for deal in store_deals:
                product = deal['product']
                price = f"${deal['price']}" if isinstance(deal['price'], (int, float)) else deal['price']
                discount = deal['discount']
                
                deal_line = f"   • {product}: **{price}** ({discount})\n"
                
                # Check if adding the next deal line exceeds the limit
                if len(current_message) + len(deal_line) > TELEGRAM_MESSAGE_LIMIT:
                    # Finalize the current message and start a new page
                    current_message += "\n(Message too long, continued below...)"
                    messages_to_send.append(current_message)
                    
                    # Start new page, re-adding the main and store headers
                    current_message = f"🛒 **Weekly Grocery Deals Alert! (Cont.)** 🛒\n\n"
                    current_message += store_header 

                current_message += deal_line
            
            current_message += "\n" # Add a space between stores

        # Add the last partially filled message
        if current_message.strip():
            messages_to_send.append(current_message)

        # Update the header in all messages with the final page count
        num_pages = len(messages_to_send)
        for i, msg in enumerate(messages_to_send):
            # Prepend the pagination info to the beginning of the message
            messages_to_send[i] = f"Page {i + 1} of {num_pages} | {msg}"

    # 4. SEND NOTIFICATION (Iterate
