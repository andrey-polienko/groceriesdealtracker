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

                store_name = item.get('merchant_name', 'Unknown Store')
                
                # FIX: Defensive coding against NoneType error (Handles null values from API)
                item_name = str(item.get('flyer_item_description') or '').lower()
                product_name = str(item.get('name') or '').lower()
                
                # Check if the deal matches the current search keyword
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
            
            # DEBUG LOGGING
            print(f"   -> Total unique deals found so far: {len(all_found_items)}")


        except requests.exceptions.RequestException as e:
            print(f"Error fetching data for {search_keyword}: {e}")
            
    return list(all_found_items.values())


async def send_notification(deals):
    """Formats and sends the deals list via Telegram."""
    if not deals:
        message = "No new deals found for your interests this week!"
    else:
        # Group deals by store
        stores = {}
        for deal in deals:
            store = deal['store']
            if store not in stores:
                stores[store] = []
            stores[store].append(deal)

        # Format the final message
        message = "🛒 **Weekly Grocery Deals Alert!** 🛒\n\n"
        for store, store_deals in stores.items():
            message += f"--- 🏢 **{store}** ---\n"
            for deal in store_deals:
                product = deal['product']
                # Correctly format price
                price = f"${deal['price']}" if isinstance(deal['price'], (int, float)) else deal['price']
                discount = deal['discount']

                message += f"   • {product}: **{price}** ({discount})\n"
            message += "\n"

    # 4. SEND NOTIFICATION
    if BOT_TOKEN and CHAT_ID:
        try:
            bot = Bot(token=BOT_TOKEN)
            await bot.send_message(chat_id=CHAT_ID, text=message, parse_mode='Markdown')
        except Exception as e:
            print(f"Error sending Telegram message: {e}")
    else:
        print("Error: BOT_TOKEN or CHAT_ID is missing. Cannot send Telegram message.")


if __name__ == "__main__":
    print("Starting grocery deal tracker...")

    # We need to run the async function using asyncio.run()
    deals = get_deals()
    asyncio.run(send_notification(deals))

    print(f"Finished. Found {len(deals)} deals.")
