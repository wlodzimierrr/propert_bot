import pandas as pd
import os
from datetime import datetime
from glob import glob
import telebot
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Get the directory where the script is located and navigate to data folder
app_dir = os.path.abspath(os.path.join(os.path.dirname(__file__)))
data_dir = os.path.join(app_dir, 'data')
sent_properties_file = os.path.join(app_dir, 'sent_properties.csv')

# Create sent_properties.csv if it doesn't exist
if not os.path.exists(sent_properties_file):
    pd.DataFrame(columns=['propertyUrl', 'displayAddress', 'propertySubType', 'price.amount', 
                         'bedrooms', 'addedOrReduced', 'addedOrReducedDate', 'date_sent']).to_csv(sent_properties_file, index=False)

# List all CSV files in the directory
csv_files = glob(os.path.join(data_dir, '*.csv'))

# Get the most recent file
latest_file = max(csv_files, key=os.path.getmtime)

# Read the CSV files
df = pd.read_csv(latest_file)
sent_properties = pd.read_csv(sent_properties_file)

# Filter out apartments, flats, park homes and land
excluded_types = ['Apartment', 'Flat', 'Park Home', 'Land', 'Retirement Property','Ground Flat']
filtered_df = df[~df['propertySubType'].isin(excluded_types)]

# Filter out already sent properties
new_properties = filtered_df[~filtered_df['propertyUrl'].isin(sent_properties['propertyUrl'])]

# Initialize the bot with your token
bot = telebot.TeleBot(os.getenv('TELEGRAM_BOT_TOKEN'))
CHAT_ID = os.getenv('TELEGRAM_CHAT_ID')

def escape_markdown(text):
    """Escape markdown special characters"""
    if not isinstance(text, str):
        text = str(text)
    escape_chars = r'_*[]()~`>#+-=|{}.!'
    return ''.join(f'\\{c}' if c in escape_chars else c for c in text)

# Format the property information into a readable message
def format_property_message(property_row):
    message = (
        "🏠 New Property Listed!\n\n"
        f"Address: {escape_markdown(property_row['displayAddress'])}\n"
        f"Type: {escape_markdown(property_row['propertySubType'])}\n"
        f"Price: £{property_row['price.amount']:,}\n"
        f"Bedrooms: {property_row['bedrooms']}\n"
        f"Status: {escape_markdown(property_row['addedOrReduced'])}\n"
        f"Date: {escape_markdown(str(property_row['addedOrReducedDate']))}\n\n"
        f"{property_row['propertyUrl']}"
    )
    return message

# List to store successfully sent properties
successfully_sent = []

# Send message for each new property
for _, property_row in new_properties.iterrows():
    message = format_property_message(property_row)
    try:
        bot.send_message(CHAT_ID, message, parse_mode=None)
        print(f"Message sent successfully for property: {property_row['displayAddress']}")
        
        # Add to successfully sent list
        property_data = property_row.to_dict()
        property_data['date_sent'] = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
        successfully_sent.append(property_data)
        
    except Exception as e:
        print(f"Error sending message: {e}")

# Update sent_properties.csv with new sent properties
if successfully_sent:
    new_sent_df = pd.DataFrame(successfully_sent)
    updated_sent_properties = pd.concat([sent_properties, new_sent_df], ignore_index=True)
    updated_sent_properties.to_csv(sent_properties_file, index=False)
    print(f"Added {len(successfully_sent)} new properties to sent_properties.csv")
else:
    print("No new properties to send")