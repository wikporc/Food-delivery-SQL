import pandas as pd
import matplotlib.pyplot as plt
import os
import re
import math

def analyze_pizza_prices_combined(combined_restaurants_csv, combined_menu_items_csv, output_dir='analysis/combined'):
    """
    Analyzes the price per square centimeter of pizzas from the combined dataset,
    handling both circular and rectangular pizzas, and generates a histogram.

    Args:
        combined_restaurants_csv (str): Path to the combined restaurants CSV.
        combined_menu_items_csv (str): Path to the combined menu items CSV.
        output_dir (str): The directory to save the histogram image.
    """
    print("Analyzing pizza prices (price per cm²) for combined platforms...")
    df_restaurants = pd.read_csv(combined_restaurants_csv)
    # Explicitly specify dtype for 'restaurant_id' to avoid DtypeWarning if it's mixed in some rows
    df_menu_items = pd.read_csv(combined_menu_items_csv, dtype={'restaurant_id': str, 'price': float})

    # Filter menu items for pizza
    pizza_menu_items = df_menu_items[(df_menu_items['menu_item_name'].str.contains('pizza', case=False, na=False)) |
                                     (df_menu_items['description'].str.contains('pizza', case=False, na=False))].copy()
    
    # Ensure price is numeric and positive
    pizza_menu_items['price'] = pd.to_numeric(pizza_menu_items['price'], errors='coerce')
    pizza_menu_items.dropna(subset=['price'], inplace=True)
    pizza_menu_items = pizza_menu_items[pizza_menu_items['price'] > 0]

    # Merge with restaurant names and platform. Pandas renames 'platform' to 'platform_x' and 'platform_y'
    # We want the platform of the restaurant itself.
    merged_pizza_data = pd.merge(pizza_menu_items, 
                                 df_restaurants[['restaurant_id_platform_unique', 'restaurant_name', 'platform']],
                                 on='restaurant_id_platform_unique', how='left')

    # Rename platform_y to a single 'platform' column and drop platform_x if it exists and is different
    # In this merge, platform_x comes from menu_items and platform_y from restaurants.
    # We should rely on the platform from the restaurant data.
    merged_pizza_data.rename(columns={'platform_y': 'platform'}, inplace=True)
    if 'platform_x' in merged_pizza_data.columns:
        merged_pizza_data.drop(columns=['platform_x'], inplace=True)


    pizza_analysis = []
    rect_regex = re.compile(r'(\d+)\s*x\s*(\d+)\s*cm')
    circ_regex = re.compile(r'(\d+)\s*cm')

    for index, row in merged_pizza_data.iterrows():
        search_text = f"{row['menu_item_name']} {row['description']}"
        
        rect_match = rect_regex.search(search_text)
        circ_match = circ_regex.search(search_text)

        area = 0
        size_str = ""

        if rect_match:
            width = int(rect_match.group(1))
            length = int(rect_match.group(2))
            area = width * length
            size_str = f"{width}x{length}cm"
        elif circ_match:
            diameter = int(circ_match.group(1))
            if diameter > 0:
                radius = diameter / 2
                area = math.pi * (radius ** 2)
                size_str = f"{diameter}cm"

        if area > 0: # Price already filtered to be > 0
            price_per_sq_cm = row['price'] / area
            pizza_analysis.append((row['restaurant_name'], row['menu_item_name'], row['price'], 
                                   size_str, area, price_per_sq_cm, row['platform']))

    if not pizza_analysis:
        print("No valid pizza data with size information found for combined platforms.")
        return

    # Sort by price per square centimeter in ascending order (best value first)
    pizza_analysis.sort(key=lambda x: x[5])

    os.makedirs(output_dir, exist_ok=True) # Ensure output directory exists

    # Generate and save histogram
    prices_per_cm2 = [item[5] for item in pizza_analysis]
    if prices_per_cm2:
        plt.figure(figsize=(10, 6))
        plt.hist(prices_per_cm2, bins=150, edgecolor='black', range=(0, 0.06)) # Set a reasonable range
        plt.title('Distribution of Pizza Price per cm² (Combined Platforms)')
        plt.xlabel('Price per cm² (€)')
        plt.ylabel('Number of Pizzas')
        plt.grid(axis='y', alpha=0.75)
        plt.savefig(os.path.join(output_dir, 'price_per_cm2_distribution.png'))
        plt.close()

    print("\nTop 10 Best Value Pizzas (Price per cm² - Combined Platforms):")
    for i, pizza in enumerate(pizza_analysis[:10], 1):
        print(f"{i}. Restaurant: {pizza[0]} (Platform: {pizza[6]})")
        print(f"   Pizza: {pizza[1]}")
        print(f"   Price: €{pizza[2]:.2f}, Size: {pizza[3]}, Surface: {pizza[4]:.2f}cm²")
        print(f"   Price per cm²: €{pizza[5]:.4f}")
        print("-" * 20)

if __name__ == '__main__':
    combined_restaurants_csv = 'analysis/combined/all_restaurants.csv'
    combined_menu_items_csv = 'analysis/combined/all_menu_items.csv'
    analyze_pizza_prices_combined(combined_restaurants_csv, combined_menu_items_csv)