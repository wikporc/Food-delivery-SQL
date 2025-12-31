import pandas as pd
import geopandas as gpd
import matplotlib.pyplot as plt
import os
import re
import math

# Paths
COMBINED_RESTAURANTS_CSV = 'analysis/combined/all_restaurants.csv'
COMBINED_MENU_ITEMS_CSV = 'analysis/combined/all_menu_items.csv'
SHAPEFILE_PATH = 'shapefiles/Belgium-4-Digit-Postcodes-2020.shp'
OUTPUT_MAP_PATH = 'analysis/combined/pizza_value_choropleth_map.png'

def analyze_pizza_prices_by_postal_code_for_map_combined(combined_restaurants_csv, combined_menu_items_csv, min_pizza_count=3):
    """
    Analyzes the average price per square centimeter of pizzas by postal code for combined platforms.
    """
    print("Analyzing pizza prices by postal code for combined platforms map...")
    df_restaurants = pd.read_csv(combined_restaurants_csv)
    df_menu_items = pd.read_csv(combined_menu_items_csv, dtype={'restaurant_id': str, 'price': float})

    # Filter menu items for pizza
    pizza_menu_items = df_menu_items[(df_menu_items['menu_item_name'].str.contains('pizza', case=False, na=False)) |
                                     (df_menu_items['description'].str.contains('pizza', case=False, na=False))].copy()
    
    # Ensure price is numeric and positive
    pizza_menu_items['price'] = pd.to_numeric(pizza_menu_items['price'], errors='coerce')
    pizza_menu_items.dropna(subset=['price'], inplace=True)
    pizza_menu_items = pizza_menu_items[pizza_menu_items['price'] > 0]

    # Merge pizza menu items with restaurant data (including postalCode)
    # Use restaurant_id_platform_unique for merging
    merged_df = pd.merge(pizza_menu_items, df_restaurants[['restaurant_id_platform_unique', 'postalCode']],
                         on='restaurant_id_platform_unique', how='left')
    
    merged_df.dropna(subset=['postalCode'], inplace=True) # Drop if postalCode is missing

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
                size_str = f"{diameter}cm"

        if area > 0 and price > 0:
            price_per_sq_cm = price / area
            try:
                postal_code_int = int(float(row['postalCode']))
                pizza_data.append({'postalCode': postal_code_int, 'price_per_sq_cm': price_per_sq_cm})
            except (ValueError, TypeError):
                pass # Skip if postalCode is not a valid number


    if not pizza_data:
        print("No valid pizza data with size information found for combined platforms.")
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

def generate_pizza_value_choropleth_map_combined(combined_restaurants_csv, combined_menu_items_csv, output_path=OUTPUT_MAP_PATH, min_pizza_count=3):
    """
    Generates a choropleth map of Belgium showing average pizza price per cm² by postal code for combined platforms.
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
    pizza_postal_code_data = analyze_pizza_prices_by_postal_code_for_map_combined(combined_restaurants_csv, combined_menu_items_csv, min_pizza_count)

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
    ax.set_title('Average Pizza Price per cm² by Postal Code in Belgium (Combined Platforms)', fontdict={'fontsize': '16', 'fontweight': '3'})
    ax.set_axis_off()
    
    os.makedirs(os.path.dirname(output_path), exist_ok=True)
    plt.savefig(output_path, dpi=300)
    plt.close()

    print(f"Choropleth map saved to: {output_path}")

if __name__ == '__main__':
    generate_pizza_value_choropleth_map_combined(COMBINED_RESTAURANTS_CSV, COMBINED_MENU_ITEMS_CSV, min_pizza_count=3)
