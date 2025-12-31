import sqlite3
import pandas as pd
import matplotlib.pyplot as plt
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

def analyze_restaurants_per_location_deliveroo(db_path, output_dir='analysis/deliveroo'):
    """
    Analyzes how restaurants are distributed across different cities on the Deliveroo platform.

    Args:
        db_path (str): The path to the SQLite database file.
        output_dir (str): The directory to save the generated plots.
    """
    conn = sqlite3.connect(db_path)

    query_city = """
    SELECT
        postal_code,
        id AS restaurant_id
    FROM
        restaurants
    WHERE
        postal_code IS NOT NULL AND postal_code != ''
    """
    df_restaurants = pd.read_sql_query(query_city, conn)

    conn.close()

    # Apply standardization
    df_restaurants['standardized_city'] = df_restaurants['postal_code'].apply(get_standardized_city)
    df_restaurants.dropna(subset=['standardized_city'], inplace=True) # Drop rows where city could not be standardized

    if df_restaurants.empty:
        print("No restaurants with standardized cities found. Cannot generate report.")
        return

    # Now group by the standardized city
    df_city = df_restaurants.groupby('standardized_city').agg(
        restaurant_count=('restaurant_id', 'nunique') # Use restaurant_id to count unique restaurants
    ).reset_index()
    df_city.rename(columns={'standardized_city': 'city'}, inplace=True)
    df_city.sort_values(by='restaurant_count', ascending=False, inplace=True)

    if df_city.empty:
        print("\nNo cities found after standardization and grouping. Check postal code mapping.")
        return

    total_for_percentage = df_city['restaurant_count'].sum()
    df_city['percentage'] = (df_city['restaurant_count'] / total_for_percentage) * 100

    os.makedirs(output_dir, exist_ok=True) # Ensure output directory exists

    # --- Visualization 1: Top 20 cities by number of restaurants ---
    top_20 = df_city.head(20)
    plt.figure(figsize=(12, 8))
    plt.barh(top_20['city'], top_20['restaurant_count'], color='skyblue')
    plt.xlabel('Number of Unique Restaurants')
    plt.ylabel('City')
    plt.title('Top 20 Cities by Number of Unique Restaurants (Deliveroo - Standardized)')
    plt.gca().invert_yaxis()
    plt.tight_layout()
    plt.savefig(os.path.join(output_dir, 'restaurants_per_location.png'))
    plt.close()

    # --- Visualization 2: Concentration of restaurants ---
    top_10_pie = df_city.head(10).copy()
    other_percentage = df_city['percentage'][10:].sum()
    if other_percentage > 0:
        top_10_pie.loc[len(top_10_pie)] = {'city': 'Other', 'restaurant_count': 0, 'percentage': other_percentage}


    plt.figure(figsize=(10, 10))
    plt.pie(top_10_pie['percentage'], labels=top_10_pie['city'], autopct='%1.1f%%', startangle=140)
    plt.title('Restaurant Concentration in Top 10 Cities (Deliveroo - Standardized)')
    plt.axis('equal')
    plt.savefig(os.path.join(output_dir, 'restaurants_concentration.png'))
    plt.close()

    print("\nTop 10 cities with most unique restaurants (Deliveroo - Standardized):")
    print(df_city.head(10).to_markdown(index=False))

    print(f"\nNote: Percentages are relative to the total number of unique restaurants in the dataset.")

if __name__ == '__main__':
    db_path = 'databases/deliveroo.db'
    analyze_restaurants_per_location_deliveroo(db_path)
