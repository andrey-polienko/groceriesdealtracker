import os
import requests
from telegram import Bot
import asyncio

# *** 1. CONFIGURATION (MUST CHANGE THESE) ***
POSTAL_CODE = 'M2N 7J6'  # e.g., 'M5V 2L9'
DEALS_OF_INTEREST = ['meat', 'apple', 'snack'] # e.g., ['chicken breast', 'banana', 'cookies']

# Read secrets from GitHub Actions environment variables
BOT_TOKEN = os.environ.get('TELEGRAM_BOT_TOKEN', 'YOUR_BOT_TOKEN_FOR_LOCAL_TESTING') # Replace placeholder if testing locally
CHAT_ID = os.environ.get('39354851', 'YOUR_CHAT_ID')   # Replace placeholder if testing locally

# Flipp's unofficial API endpoint - retrieves raw deal data
FLIPP_API_URL = f"https://backflipp.wishabi.com/flipp/items/search?locale=en-ca&postal_code={POSTAL_CODE}"


def get_deals():
    """Fetches and filters deals from the Flipp API."""
    try:
        # 2. GET FLYER DATA
        response = requests.get(FLIPP_API_URL, params={'q': 'deals'}, timeout=10)
        response.raise_for_status()
        data = response.json()

        # 3. PROCESS AND FILTER DEALS
        found_deals = []
        for item in data.get('items', []):
            item_name = item.get('flyer_item_description', '').lower()
            store_name = item.get('merchant_name', 'Unknown Store')

            # Check if the deal matches any of your keywords
            is_match = False
            for keyword in DEALS_OF_INTEREST:
                if keyword.lower() in item_name:
                    is_match = True
                    break

            if is_match:
                price = item.get('current_price', 'Price Not Listed')
                discount = item.get('pre_price_text', '') # Often contains "Save $X" or percentage

                found_deals.append({
                    'product': item.get('name', 'N/A'),
                    'store': store_name,
                    'price': price,
                    'discount': discount,
                    'description': item_name
                })

        return found_deals

    except requests.exceptions.RequestException as e:
        print(f"Error fetching data: {e}")
        return []


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
                price = f"${deal['price']}" if isinstance(deal['price'], (int, float)) else deal['price']
                discount = deal['discount']

                # Logistical Note: You would calculate logistics here, but for now we just list them.

                message += f"   • {product}: **{price}** ({discount})\n"
            message += "\n"

    # 4. SEND NOTIFICATION
    if BOT_TOKEN and CHAT_ID:
        bot = Bot(token=BOT_TOKEN)
        await bot.send_message(chat_id=CHAT_ID, text=message, parse_mode='Markdown')
    else:
        print("Error: BOT_TOKEN or CHAT_ID is missing. Cannot send Telegram message.")


if __name__ == "__main__":
    print("Starting grocery deal tracker...")

    # We need to run the async function using asyncio.run()
    deals = get_deals()
    asyncio.run(send_notification(deals))


    print(f"Finished. Found {len(deals)} deals.")
