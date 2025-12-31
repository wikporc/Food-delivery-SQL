import sqlite3
import re
import math
import pandas as pd
import geopandas as gpd
import matplotlib.pyplot as plt
import requests
import os
import time
import json
from tqdm import tqdm

CACHE_FILE_NAME = 'geocode_cache.json'
RESTAURANT_POSTAL_CODES_CSV = 'analysis/takeaway/restaurant_postal_codes.csv'
SHAPEFILE_PATH = 'shapefiles/Belgium-4-Digit-Postcodes-2020.shp'

def load_cache(temp_dir):
    cache_file_path = os.path.join(temp_dir, CACHE_FILE_NAME)
    if os.path.exists(cache_file_path):
        with open(cache_file_path, 'r') as f:
            return json.load(f)
    return {}

def save_cache(cache, temp_dir):
    cache_file_path = os.path.join(temp_dir, CACHE_FILE_NAME)
    with open(cache_file_path, 'w') as f:
        json.dump(cache, f)

def get_postal_code(lon, lat, cache):
    """
    Reverse geocode coordinates to a postal code using Nominatim API with caching.
    """
    cache_key = f"{lon},{lat}"
    if cache_key in cache:
        return cache[cache_key]

    if lon == 0 and lat == 0:
        cache[cache_key] = None
        return None
    
    url = f"https://nominatim.openstreetmap.org/reverse?format=json&lat={lat}&lon={lon}"
    headers = {
        'User-Agent': 'Chrome/143.0.0.0'
    }
    try:
        response = requests.get(url, headers=headers)
        response.raise_for_status()
        data = response.json()
        time.sleep(1) # To respect Nominatim's usage policy (max 1 req/sec)
        if 'address' in data and 'postcode' in data['address']:
            postcode = data['address']['postcode']
            cache[cache_key] = postcode
            return postcode
    except requests.exceptions.RequestException as e:
        print(f"Error geocoding ({lon}, {lat}): {e}")
    
    cache[cache_key] = None # Cache non-found results too
    return None

def analyze_pizza_prices_by_postal_code_for_map(db_path, min_pizza_count=10):
    """
    Analyzes the average price per square centimeter of pizzas by postal code.
    Reads restaurant postal codes from a pre-generated CSV.
    """
    conn = sqlite3.connect(db_path)

    # Load restaurant postal codes from the pre-generated CSV
    if not os.path.exists(RESTAURANT_POSTAL_CODES_CSV):
        print(f"Error: {RESTAURANT_POSTAL_CODES_CSV} not found. Please run 6_geocode_restaurants.py first.")
        return pd.DataFrame(columns=['postalCode', 'avg_price_per_sq_cm', 'pizza_count'])
        
    restaurants_postal_codes_df = pd.read_csv(RESTAURANT_POSTAL_CODES_CSV)
    
    # Get pizza data
    pizzas_query = """
        SELECT
            mi.primarySlug,
            mi.name,
            mi.price,
            mi.description
        FROM
            menuItems mi
        WHERE
            (mi.name LIKE '%pizza%')
            AND (mi.description LIKE '%cm%' OR mi.name LIKE '%cm%');
    """
    pizzas_df = pd.read_sql_query(pizzas_query, conn)
    conn.close()
    
    # Merge pizza data with restaurant postal codes
    # Ensure primarySlug in restaurants_postal_codes_df is not null
    restaurants_postal_codes_df = restaurants_postal_codes_df.dropna(subset=['primarySlug'])
    merged_df = pd.merge(pizzas_df, restaurants_postal_codes_df, on='primarySlug')
    merged_df = merged_df.dropna(subset=['postalCode'])


    pizza_data = []
    rect_regex = re.compile(r'(\d+)\s*x\s*(\d+)\s*cm')
    circ_regex = re.compile(r'(\d+)\s*cm')

    for index, row in merged_df.iterrows():
        search_text = f"{row['name']} {row['description']}"
        
        rect_match = rect_regex.search(search_text)
        circ_match = circ_regex.search(search_text)

        area = 0
        if rect_match:
            width = int(rect_match.group(1))
            length = int(rect_match.group(2))
            area = width * length
        elif circ_match:
            diameter = int(circ_match.group(1))
            if diameter > 0:
                radius = diameter / 2
                area = math.pi * (radius ** 2)
        
        if area > 0 and row['price'] > 0:
            price_per_sq_cm = row['price'] / area
            pizza_data.append({'postalCode': row['postalCode'], 'price_per_sq_cm': price_per_sq_cm})

    if not pizza_data:
        return pd.DataFrame(columns=['postalCode', 'avg_price_per_sq_cm', 'pizza_count'])

    pizza_df = pd.DataFrame(pizza_data)
    
    pizza_df['postalCode'] = pd.to_numeric(pizza_df['postalCode'], errors='coerce')
    pizza_df.dropna(subset=['postalCode'], inplace=True)
    pizza_df['postalCode'] = pizza_df['postalCode'].astype(int)

    postal_code_analysis = pizza_df.groupby('postalCode').agg(
        avg_price_per_sq_cm=('price_per_sq_cm', 'mean'),
        pizza_count=('price_per_sq_cm', 'size')
    ).reset_index()

    postal_code_analysis = postal_code_analysis[postal_code_analysis['pizza_count'] >= min_pizza_count]

    return postal_code_analysis

def generate_pizza_value_choropleth_map(db_path, output_path='analysis/takeaway/pizza_value_choropleth_map.png', min_pizza_count=10):
    """
    Generates a choropleth map of Belgium showing average pizza price per cm² by postal code.
    """
    # Load postal code boundaries shapefile
    if not os.path.exists(SHAPEFILE_PATH):
        print(f"Error: Shapefile not found at {SHAPEFILE_PATH}.")
        return

    belgium_map = gpd.read_file(SHAPEFILE_PATH)
        
    # Ensure postal code columns are of the same type for merging
    belgium_map['nouveau_PO'] = pd.to_numeric(belgium_map['nouveau_PO'], errors='coerce')
    belgium_map.dropna(subset=['nouveau_PO'], inplace=True)
    belgium_map['nouveau_PO'] = belgium_map['nouveau_PO'].astype(int)

    # Analyze pizza prices by postal code
    # We call analyze_pizza_prices_by_postal_code_for_map here
    pizza_postal_code_data = analyze_pizza_prices_by_postal_code_for_map(db_path, min_pizza_count)

    if pizza_postal_code_data.empty:
        print("No postal code data found after filtering.")
        return

    # Merge the GeoDataFrame with the pizza analysis data
    merged = belgium_map.set_index('nouveau_PO').join(pizza_postal_code_data.set_index('postalCode'))
    # merged = merged.dropna(subset=['avg_price_per_sq_cm']) # Remove this line to plot all postal codes

    fig, ax = plt.subplots(1, 1, figsize=(12, 12))
    
    # Plot the map
    merged.plot(column='avg_price_per_sq_cm', cmap='viridis_r', linewidth=0.8, ax=ax, edgecolor='0.8',
                legend=True, legend_kwds={'label': "Average Price per cm² (€)", 'orientation': "horizontal"},
                missing_kwds={"color": "#cccccc", "edgecolor": "red", "hatch": "///", "label": "No Pizza Data"})

    ax.set_title('Average Pizza Price per cm² by Postal Code in Belgium', fontdict={'fontsize': '16', 'fontweight': '3'})
    ax.set_axis_off()
    
    plt.savefig(output_path, dpi=300)
    plt.close()

    print(f"Choropleth map saved to: {output_path}")

if __name__ == '__main__':
    db_path = 'databases/takeaway.db'
    temp_dir = os.environ.get('temp_dir', '/tmp') # Fallback to /tmp if not set
    
    generate_pizza_value_choropleth_map(db_path)