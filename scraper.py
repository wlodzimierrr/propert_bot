import requests
import pandas as pd
from datetime import datetime
import os

# Define city codes (replace with desired city locationIdentifiers)
city_codes = {
    "Southampton": "REGION%5E1231",
    "Eastleigh": "REGION%5E471"
}

pages = 1

max_price = 180000
min_price = 0

max_bedrooms = 5
min_bedrooms = 2

# Define user headers
headers = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/89.0.4389.114 Safari/537.36"
}

output = []
for name, city_code in city_codes.items():
    for page in range(1, pages + 1):
        url = (
            f"https://www.rightmove.co.uk/api/_search?locationIdentifier={city_code}&numberOfPropertiesPerPage=24&"
            f"radius=0.0&index={24 * (page - 1)}&maxBedrooms={max_bedrooms}&minBedrooms={min_bedrooms}&"
            f"maxPrice={max_price}&minPrice={min_price}&sortType=6&propertyTypes=&includeSSTC=false&viewType=LIST&"
            f"channel=BUY&areaSizeUnit=sqft&currencyCode=GBP&isFetching=false"
        )
        print(f"Scraping: {name} - Page: {page}")

        response = requests.get(url, headers=headers)
        
        # Check if the response is JSON
        if response.headers.get('Content-Type') != 'application/json':
            print(f"Skipping non-JSON response for {name} - Page: {page}")
            continue
        
        data = response.json()
        properties = data.get('properties', [])
        
        # If no properties, skip to the next page
        if not properties:
            print(f"No properties found for {name} - Page: {page}")
            continue
        
        # Normalize properties and filter columns, make a copy to avoid SettingWithCopyWarning
        df = pd.json_normalize(properties)
        df_filtered = df[[
            'propertyUrl',           # Page URL
            'displayAddress',        # Address
            'price.amount',          # Price
            'addedOrReduced',        # Date added or reduced
            'bedrooms',              # Number of bedrooms
            'propertySubType'        # Property type
        ]].copy()
        
        # Prefix the property URL with the base URL
        df_filtered['propertyUrl'] = "https://www.rightmove.co.uk" + df_filtered['propertyUrl']

        # Split 'addedOrReduced' into two columns
        df_filtered[['addedOrReduced', 'addedOrReducedDate']] = df_filtered['addedOrReduced'].str.split(' on ', expand=True)
        
        output.append(df_filtered)

# Concatenate all data and export to CSV
# Get the directory where house_alerts is located
app_dir = os.path.abspath(os.path.join(os.path.dirname(__file__)))
# Create the full path to the data directory
save_path = os.path.join(app_dir, 'data')

# Create the data directory if it doesn't exist
os.makedirs(save_path, exist_ok=True)

# Generate filename with today's date and time
filename = datetime.now().strftime('%Y-%m-%d_%H-%M-%S') + '.csv'

# Combine path and filename
full_path = os.path.join(save_path, filename)

final_df = pd.concat(output, ignore_index=True)
final_df.to_csv(full_path, index=False)

print(f"Data saved to {filename}")
