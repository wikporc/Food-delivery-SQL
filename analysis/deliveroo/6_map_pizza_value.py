import sqlite3
import re
import math
import pandas as pd
import geopandas as gpd
import matplotlib.pyplot as plt
import os
import json # Import json for loading zipcode-belgium.json

# Paths
SHAPEFILE_PATH = 'shapefiles/Belgium-4-Digit-Postcodes-2020.shp'
OUTPUT_MAP_PATH = 'analysis/deliveroo/pizza_value_choropleth_map.png'

# Load postal code to city mapping once (for potential insights, though not directly used in choropleth merge)
POSTAL_CODE_MAP_FILE = 'analysis/zipcode-belgium.json'
postal_code_to_city = {}
if os.path.exists(POSTAL_CODE_MAP_FILE):
    with open(POSTAL_CODE_MAP_FILE, 'r', encoding='utf-8') as f:
        data = json.load(f)
        for entry in data:
            postal_code_to_city[str(entry['zip'])] = entry['city']

def analyze_pizza_prices_by_postal_code_for_map_deliveroo(db_path, min_pizza_count=1):
    """
    Analyzes the average price per square centimeter of pizzas by postal code for Deliveroo.
    Uses the postal_code directly from the restaurants table.
    """
    conn = sqlite3.connect(db_path)

    query = """
        SELECT
            r.postal_code AS postalCode,
            mi.name,
            mi.price,
            mi.description
        FROM
            menu_items mi
        JOIN
            restaurants r ON mi.restaurant_id = r.id
        WHERE
            (mi.name LIKE '%pizza%')
            AND (mi.description LIKE '%cm%' OR mi.name LIKE '%cm%')
            AND mi.price > 0
            AND r.postal_code IS NOT NULL;
    """
    df_raw = pd.read_sql_query(query, conn)
    conn.close()

    pizza_data = []
    rect_regex = re.compile(r'(\d+)\s*x\s*(\d+)\s*cm')
    circ_regex = re.compile(r'(\d+)\s*cm')

    for index, row in df_raw.iterrows():
        price = float(row['price']) # Ensure price is float
        
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
        
        if area > 0 and price > 0:
            price_per_sq_cm = price / area
            # Ensure postalCode is convertible to int
            try:
                postal_code_int = int(float(row['postalCode']))
                pizza_data.append({'postalCode': postal_code_int, 'price_per_sq_cm': price_per_sq_cm})
            except (ValueError, TypeError):
                pass # Skip if postalCode is not a valid number


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

def generate_pizza_value_choropleth_map_deliveroo(db_path, output_path=OUTPUT_MAP_PATH, min_pizza_count=1):
    """
    Generates a choropleth map of Belgium showing average pizza price per cm² by postal code for Deliveroo.
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
    pizza_postal_code_data = analyze_pizza_prices_by_postal_code_for_map_deliveroo(db_path, min_pizza_count)

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
    ax.set_title('Average Pizza Price per cm² by Postal Code in Belgium (Deliveroo)', fontdict={'fontsize': '16', 'fontweight': '3'})
    ax.set_axis_off()
    
    os.makedirs(os.path.dirname(output_path), exist_ok=True) # Ensure output directory exists
    plt.savefig(output_path, dpi=300)
    plt.close()

    print(f"Choropleth map saved to: {output_path}")

if __name__ == '__main__':
    db_path = 'databases/deliveroo.db'
    
    generate_pizza_value_choropleth_map_deliveroo(db_path, min_pizza_count=1)