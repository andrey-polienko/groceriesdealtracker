# groceriesdealtracker
🛒 Automated Weekly Grocery Deal Tracker
An automated, zero-cost pipeline that searches local grocery flyers by leveraging Flipp's digital flyer data (via an unofficial API backend). It automatically filters deals by your specific keywords and preferred stores, delivering a beautifully categorized, paginated breakdown directly to your phone via a Telegram Bot.

Runs automatically every week using GitHub Actions—no personal servers or local computer uptime required.

✨ Features
Powered by Flipp: Uses the industry-leading digital flyer aggregator to fetch comprehensive, up-to-date local supermarket specials without manual web scraping.

Custom Filtering: Tracks only the categories and exact products you care about (e.g., specific cuts of meat, organic produce, or school snacks).

Preferred Stores Only: Discards noise from retailers you don't shop at; focuses entirely on your local favorites (No Frills, Walmart, Food Basics, Loblaws, etc.).

Smart Categorization: Grouped by aisle/category (e.g., Meat/Protein, Fruit and Vegetables) and then by #Store for easy meal planning.

Automatic Pagination: Handles massive amounts of data smoothly by automatically splitting listings into sequential Telegram messages to respect API limits.

Zero Infrastructure: Powered entirely by free-tier GitHub Actions cloud schedules.

🛠️ Installation & Setup
Follow these steps to deploy your tracker over a weekend.

Phase 1: Set Up Your Telegram Bot
Open Telegram, search for @BotFather, and start a chat.

Send the command /newbot and choose a name and a username for your bot.

Copy the HTTP API Token provided (e.g., 1234567890:AABBCCDD...). This is your TELEGRAM_BOT_TOKEN.

Search for your new bot's username in Telegram, click Start, and send it a dummy message (like "Hello").

To get your unique conversation ID, open your web browser and navigate to:

Plaintext
https://api.telegram.org/bot<YOUR_BOT_TOKEN>/getUpdates
Look for the "chat" object in the text and copy the number next to "id": (it will be a large number, often negative if it's a group, e.g., -10023456789). This is your TELEGRAM_CHAT_ID.

Phase 2: Create Your GitHub Repository
Log into GitHub and create a New Repository. Set it to Private to keep your grocery list and keys hidden.

Clone or create the following directory layout in your repo:

Plaintext
├── .github/
│   └── workflows/
│       └── schedule.yml    # Automation configurations
├── main.py                 # Core tracker code
└── requirements.txt        # Python dependency manager
Phase 3: Configure GitHub Secrets
Do not hardcode your Telegram details into the script. Instead:

In your GitHub repository, go to Settings → Secrets and variables → Actions.

Click New repository secret and add:

Name: TELEGRAM_BOT_TOKEN | Value: (Your Bot Token from Phase 1)

Name: TELEGRAM_CHAT_ID | Value: (Your Chat ID from Phase 1)

⚙️ Configuration & Customization
All customizations happen directly inside the main.py configuration block:

1. Changing Your Location
Update the POSTAL_CODE variable to match your local area. The script dynamically queries Flipp's database for the flyers active in this specific zone:

Python
POSTAL_CODE = 'M2N 7J6'
2. Customizing Stores
Modify the PREFERRED_STORES list. The names must match how the merchant is officially named on Flipp (case-insensitive):

Python
PREFERRED_STORES = [
    'Food Basics',
    'No Frills',
    'Loblaws',
    'T&T Supermarket',
    "Longo's",
    'Walmart'
]
3. Adjusting Categories & Keywords
You can add entirely new sections or tweak keywords in the DEALS_OF_INTEREST dictionary. The script uses these to map raw matches into cleanly grouped sections:

Python
DEALS_OF_INTEREST = {
    "Meat/Protein": ['chicken breast', 'pork', 'beef', 'steak', 'sausage'],
    "Fruit and Vegetables": ['apple', 'banana', 'broccoli', 'carrot', 'tomato'],
    "Your Custom Category": ['keyword1', 'keyword2']
}
🚀 How to Run and Use
Automated Running
By default, the script is configured via .github/workflows/schedule.yml to run automatically every Friday at 8:00 AM UTC (which aligns perfectly with fresh weekly flyer drops in most Canadian regions).

To alter the timing, adjust the cron string in the .schedule.yml file using crontab.guru.

Manual Trigger
If you want to pull deals instantly mid-week:

Go to the Actions tab in your GitHub repository.

Select the Weekly Grocery Deal Scraper workflow from the left sidebar.

Click the Run workflow dropdown button on the right, select your branch, and click Run workflow.

📋 Sample Output
When executed successfully, your bot will send structured pages to your phone that look like this:

Page 1 of 2 | 🛒 Weekly Grocery Deals Alert!
Total Deals Found: 142

🏷️ Meat/Protein
#Walmart (2 deals)
• Prime raised without antibiotics chicken breasts: $9.94 (None)
• Your Fresh Market™ Atlantic salmon portion: $17.68 (None)

#Food Basics (3 deals)
• CHICKEN BREAST: $4.77 (None)
• PORK HALF LOIN: $1.99 (ONLY)

🏷️ Fruit and Vegetables
#No Frills (2 deals)
• TOMATOES ON THE VINE OR BROCCOLI CROWNS: $1.99 (None)
• FARMER'S MARKET™ GRAPE TOMATOES: $1.88 (None)

🔍 Troubleshooting & Technical Logs
If you notice you aren't receiving messages on schedule:

Navigate to the Actions tab in GitHub.

Click on the latest run event to see its details, then select the run-script job block.

Expand the Execute Python script line item to view runtime details.

Common Errors in Logs:
telegram.error.InvalidToken: Your TELEGRAM_BOT_TOKEN secret is copied incorrectly or hasn't been set up in GitHub Secrets.

Text is too long: This error is now bypassed automatically thanks to the built-in pagination limits (TELEGRAM_MESSAGE_LIMIT = 3500), which cleanly divides large datasets into manageable pages.

AttributeError / NoneType: The defensive wrapper str(item.get(...) or '') handles cases where flyer items contain blank/null values natively without crashing.
