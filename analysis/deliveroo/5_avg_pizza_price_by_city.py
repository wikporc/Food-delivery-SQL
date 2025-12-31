import sqlite3
import re
import math
import pandas as pd
import os
import json

# Load postal code to city mapping once
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
    """
    Returns a standardized city name for a given postal code using the pre-loaded map.
    Handles potential variations in postal code format (e.g., string vs int).
    """
    if postal_code is None:
        return None
    
    postal_code_str = str(postal_code).split('.')[0] # Handle float-like strings if any
    
    return postal_code_to_city.get(postal_code_str, None)

def analyze_avg_pizza_price_by_city_deliveroo(db_path, output_dir='analysis/deliveroo', min_pizza_count=10):
    """
    Analyzes the average price per square centimeter of pizzas by city,
    filtering for cities with a minimum number of pizza offerings on Deliveroo.

    Args:
        db_path (str): The path to the SQLite database file.
        output_dir (str): The directory to save the output CSV file.
        min_pizza_count (int): The minimum number of pizzas a city must have to be included.

    Returns:
        pd.DataFrame: A pandas DataFrame with the average price per cm² for each city,
                      sorted by the best value.
    """
    conn = sqlite3.connect(db_path)
    
    # Query pizza menu items and restaurant postal codes
    query = """
        SELECT
            r.postal_code,
            mi.restaurant_id,
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
            # Apply standardization to postal codes to get city names
            city = get_standardized_city(row['postal_code'])
            if city:
                pizza_data.append({'city': city, 'price_per_sq_cm': price_per_sq_cm})

    if not pizza_data:
        return pd.DataFrame(columns=['city', 'avg_price_per_sq_cm', 'pizza_count'])

    pizza_df = pd.DataFrame(pizza_data)

    # Group by city and calculate the average price_per_sq_cm and the count of pizzas
    city_analysis = pizza_df.groupby('city').agg(
        avg_price_per_sq_cm=('price_per_sq_cm', 'mean'),
        pizza_count=('price_per_sq_cm', 'size')
    ).reset_index()

    # Apply min_pizza_count filter
    city_analysis = city_analysis[city_analysis['pizza_count'] >= min_pizza_count]

    # Sort by average price per square centimeter (best value first)
    city_analysis = city_analysis.sort_values('avg_price_per_sq_cm').reset_index(drop=True)

    return city_analysis

if __name__ == '__main__':
    db_path = 'databases/deliveroo.db'
    output_dir = 'analysis/deliveroo'
    output_csv_path = os.path.join(output_dir, 'avg_pizza_price_by_city_all.csv')
    
    # Run with min_pizza_count=3 for consistency
    all_cities_analysis = analyze_avg_pizza_price_by_city_deliveroo(db_path, output_dir=output_dir, min_pizza_count=1) 

    print("All Cities with Average Pizza Value (Price per cm² - Deliveroo):")
    print(all_cities_analysis.to_string())

    all_cities_analysis.to_csv(output_csv_path, index=False)
    print(f"\nFull city analysis saved to: {output_csv_path}")
