import sqlite3
import pandas as pd
import os
import json
import re

# Paths for individual platform data
TAKEAWAY_DB = 'databases/takeaway.db'
UBEREATS_DB = 'databases/ubereats.db'
DELIVEROO_DB = 'databases/deliveroo.db'

TAKEAWAY_RESTAURANT_POSTAL_CODES_CSV = 'analysis/takeaway/restaurant_postal_codes.csv'
UBEREATS_RESTAURANT_POSTAL_CODES_CSV = 'analysis/ubereats/restaurant_postal_codes.csv'

# Common postal code to city mapping for standardization
POSTAL_CODE_MAP_FILE = 'analysis/zipcode-belgium.json'
postal_code_to_city = {}
if os.path.exists(POSTAL_CODE_MAP_FILE):
    with open(POSTAL_CODE_MAP_FILE, 'r', encoding='utf-8') as f:
        data = json.load(f)
        for entry in data:
            postal_code_to_city[str(entry['zip'])] = entry['city']
else:
    print(f"Warning: {POSTAL_CODE_MAP_FILE} not found. City standardization might be inaccurate.")

def get_standardized_city(postal_code):
    if postal_code is None:
        return None
    postal_code_str = str(postal_code).split('.')[0]
    return postal_code_to_city.get(postal_code_str, None)

def load_and_clean_takeaway(db_path, postal_codes_csv_path):
    conn = sqlite3.connect(db_path)
    restaurants_df = pd.read_sql_query("SELECT primarySlug, name, ratings, ratingsNumber, longitude, latitude FROM restaurants", conn)
    menu_items_df = pd.read_sql_query("SELECT primarySlug, name, price, description FROM menuItems", conn)
    conn.close()

    # Rename columns to a common schema
    restaurants_df.rename(columns={'primarySlug': 'restaurant_id', 'name': 'restaurant_name', 
                                   'ratings': 'rating', 'ratingsNumber': 'review_count'}, inplace=True)
    menu_items_df.rename(columns={'primarySlug': 'restaurant_id', 'name': 'menu_item_name'}, inplace=True)
    
    # Load geocoded postal codes
    geocoded_postal_codes = pd.read_csv(postal_codes_csv_path)
    geocoded_postal_codes.rename(columns={'primarySlug': 'restaurant_id'}, inplace=True)
    restaurants_df = pd.merge(restaurants_df, geocoded_postal_codes[['restaurant_id', 'postalCode']], on='restaurant_id', how='left')

    # Add platform identifier
    restaurants_df['platform'] = 'takeaway'
    menu_items_df['platform'] = 'takeaway'

    return restaurants_df, menu_items_df

def load_and_clean_ubereats(db_path, postal_codes_csv_path):
    conn = sqlite3.connect(db_path)
    restaurants_df = pd.read_sql_query("SELECT id, title, rating__rating_value, rating__review_count, location__longitude, location__latitude FROM restaurants", conn)
    menu_items_df = pd.read_sql_query("SELECT restaurant_id, name, price, description FROM menu_items", conn)
    conn.close()

    # Rename columns to a common schema
    restaurants_df.rename(columns={'id': 'restaurant_id', 'title': 'restaurant_name', 
                                   'rating__rating_value': 'rating', 'rating__review_count': 'review_count',
                                   'location__longitude': 'longitude', 'location__latitude': 'latitude'}, inplace=True)
    menu_items_df.rename(columns={'name': 'menu_item_name'}, inplace=True)

    # Convert Uber Eats prices from cents to euros
    menu_items_df['price'] = pd.to_numeric(menu_items_df['price'], errors='coerce') / 100.0

    # Load geocoded postal codes
    geocoded_postal_codes = pd.read_csv(postal_codes_csv_path)
    geocoded_postal_codes.rename(columns={'primarySlug': 'restaurant_id'}, inplace=True)
    restaurants_df = pd.merge(restaurants_df, geocoded_postal_codes[['restaurant_id', 'postalCode']], on='restaurant_id', how='left')
    
    # Clean up review_count as it can be text like '500+'
    restaurants_df['review_count'] = pd.to_numeric(restaurants_df['review_count'], errors='coerce').fillna(0).astype(int)

    # Add platform identifier
    restaurants_df['platform'] = 'ubereats'
    menu_items_df['platform'] = 'ubereats'

    return restaurants_df, menu_items_df

def load_and_clean_deliveroo(db_path):
    conn = sqlite3.connect(db_path)
    restaurants_df = pd.read_sql_query("SELECT id, name, rating, rating_number, latitude, longitude, postal_code FROM restaurants", conn)
    menu_items_df = pd.read_sql_query("SELECT restaurant_id, name, price, description FROM menu_items", conn)
    conn.close()

    # Rename columns to a common schema
    restaurants_df.rename(columns={'id': 'restaurant_id', 'name': 'restaurant_name', 
                                   'rating_number': 'review_count'}, inplace=True)
    menu_items_df.rename(columns={'name': 'menu_item_name'}, inplace=True)

    # Deliveroo prices are already in euros
    restaurants_df.rename(columns={'postal_code': 'postalCode'}, inplace=True)
    
    # Clean up rating_number which can be text like '500+'
    restaurants_df['review_count'] = restaurants_df['review_count'].astype(str).str.replace('+', '').replace('NaN', '0')
    restaurants_df['review_count'] = pd.to_numeric(restaurants_df['review_count'], errors='coerce').fillna(0).astype(int)

    # Add platform identifier
    restaurants_df['platform'] = 'deliveroo'
    menu_items_df['platform'] = 'deliveroo'

    return restaurants_df, menu_items_df

def consolidate_all_data(output_combined_dir):
    print("Consolidating data from Takeaway, Uber Eats, and Deliveroo...")

    # Load and clean data for each platform
    takeaway_restaurants, takeaway_menu_items = load_and_clean_takeaway(TAKEAWAY_DB, TAKEAWAY_RESTAURANT_POSTAL_CODES_CSV)
    ubereats_restaurants, ubereats_menu_items = load_and_clean_ubereats(UBEREATS_DB, UBEREATS_RESTAURANT_POSTAL_CODES_CSV)
    deliveroo_restaurants, deliveroo_menu_items = load_and_clean_deliveroo(DELIVEROO_DB)

    # Consolidate restaurants
    all_restaurants = pd.concat([takeaway_restaurants, ubereats_restaurants, deliveroo_restaurants], ignore_index=True)
    all_restaurants['restaurant_id_platform_unique'] = all_restaurants['platform'] + '_' + all_restaurants['restaurant_id'].astype(str)
    
    # Apply standardized city name using the loaded postal_code_to_city map
    all_restaurants['postalCode'] = pd.to_numeric(all_restaurants['postalCode'], errors='coerce')
    all_restaurants.dropna(subset=['postalCode'], inplace=True) # Drop restaurants without valid postal codes
    all_restaurants['postalCode'] = all_restaurants['postalCode'].astype(int)
    all_restaurants['standardized_city'] = all_restaurants['postalCode'].apply(get_standardized_city)
    all_restaurants.dropna(subset=['standardized_city'], inplace=True) # Drop if standardized city not found

    # Consolidate menu items
    all_menu_items = pd.concat([takeaway_menu_items, ubereats_menu_items, deliveroo_menu_items], ignore_index=True)
    all_menu_items['restaurant_id_platform_unique'] = all_menu_items['platform'] + '_' + all_menu_items['restaurant_id'].astype(str)

    # Ensure output directory exists
    os.makedirs(output_combined_dir, exist_ok=True)

    # Save consolidated data
    all_restaurants_path = os.path.join(output_combined_dir, 'all_restaurants.csv')
    all_menu_items_path = os.path.join(output_combined_dir, 'all_menu_items.csv')
    
    all_restaurants.to_csv(all_restaurants_path, index=False)
    all_menu_items.to_csv(all_menu_items_path, index=False)

    print(f"Consolidated restaurants saved to: {all_restaurants_path}")
    print(f"Consolidated menu items saved to: {all_menu_items_path}")
    print(f"Total consolidated restaurants: {len(all_restaurants)}")
    print(f"Total consolidated menu items: {len(all_menu_items)}")

if __name__ == '__main__':
    output_combined_dir = 'analysis/combined'
    consolidate_all_data(output_combined_dir)