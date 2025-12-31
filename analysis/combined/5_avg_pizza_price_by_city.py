import pandas as pd
import os
import re
import math

# Paths
COMBINED_RESTAURANTS_CSV = 'analysis/combined/all_restaurants.csv'
COMBINED_MENU_ITEMS_CSV = 'analysis/combined/all_menu_items.csv'
OUTPUT_CSV_PATH = 'analysis/combined/avg_pizza_price_by_city_all.csv'


def analyze_avg_pizza_price_by_city_combined(combined_restaurants_csv, combined_menu_items_csv, output_dir='analysis/combined', min_pizza_count=3):
    """
    Analyzes the average price per square centimeter of pizzas by standardized city
    across combined platforms.

    Args:
        combined_restaurants_csv (str): Path to the combined restaurants CSV file.
        combined_menu_items_csv (str): Path to the combined menu items CSV file.
        output_dir (str): The directory to save the output CSV file.
        min_pizza_count (int): The minimum number of pizzas a city must have to be included.

    Returns:
        pd.DataFrame: A pandas DataFrame with the average price per cm² for each city,
                      sorted by the best value.
    """
    print("Analyzing average pizza price by standardized city for combined platforms...")
    df_restaurants = pd.read_csv(combined_restaurants_csv)
    df_menu_items = pd.read_csv(combined_menu_items_csv, dtype={'restaurant_id': str, 'price': float})

    # Filter menu items for pizza
    pizza_menu_items = df_menu_items[(df_menu_items['menu_item_name'].str.contains('pizza', case=False, na=False)) |
                                     (df_menu_items['description'].str.contains('pizza', case=False, na=False))].copy()
    
    # Ensure price is numeric and positive
    pizza_menu_items['price'] = pd.to_numeric(pizza_menu_items['price'], errors='coerce')
    pizza_menu_items.dropna(subset=['price'], inplace=True)
    pizza_menu_items = pizza_menu_items[pizza_menu_items['price'] > 0]

    # Merge pizza menu items with restaurant data (including standardized city)
    merged_df = pd.merge(pizza_menu_items, df_restaurants[['restaurant_id_platform_unique', 'standardized_city']],
                         on='restaurant_id_platform_unique', how='left')
    
    merged_df.dropna(subset=['standardized_city'], inplace=True) # Drop if standardized city is missing

    pizza_data = []
    rect_regex = re.compile(r'(\d+)\s*x\s*(\d+)\s*cm')
    circ_regex = re.compile(r'(\d+)\s*cm')

    for index, row in merged_df.iterrows():
        price = row['price']
        
        search_text = f"{row['menu_item_name']} {row['description']}"
        
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
            pizza_data.append({'city': row['standardized_city'], 'price_per_sq_cm': price_per_sq_cm})

    if not pizza_data:
        print("No valid pizza data with size information found for combined platforms.")
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
    all_cities_analysis = analyze_avg_pizza_price_by_city_combined(COMBINED_RESTAURANTS_CSV, COMBINED_MENU_ITEMS_CSV, min_pizza_count=3) 

    if not all_cities_analysis.empty:
        print("All Cities with Average Pizza Value (Price per cm² - Combined Platforms):")
        print(all_cities_analysis.to_string())

        os.makedirs(os.path.dirname(OUTPUT_CSV_PATH), exist_ok=True)
        all_cities_analysis.to_csv(OUTPUT_CSV_PATH, index=False)
        print(f"\nFull city analysis saved to: {OUTPUT_CSV_PATH}")
    else:
        print("No cities found after filtering for combined platforms.")