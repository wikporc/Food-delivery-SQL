import pandas as pd
import os

# Paths
COMBINED_MENU_ITEMS_CSV = 'analysis/combined/all_menu_items.csv'
OUTPUT_CSV_PATH = 'analysis/combined/all_pizza_menu_items.csv'

def export_all_pizza_menu_items_combined(combined_menu_items_csv, output_csv_path, output_dir='analysis/combined'):
    """
    Queries the combined menu items data for all menu items containing 'pizza'
    in their name or description and exports them to a CSV file.

    Args:
        combined_menu_items_csv (str): Path to the combined menu items CSV.
        output_csv_path (str): Path to save the output CSV file.
        output_dir (str): The directory to ensure exists for output.
    """
    print("Exporting all pizza menu items from combined platforms...")
    df_menu_items = pd.read_csv(combined_menu_items_csv, dtype={'restaurant_id': str, 'price': float})

    # Filter menu items for pizza
    pizza_menu_items = df_menu_items[(df_menu_items['menu_item_name'].str.contains('pizza', case=False, na=False)) |
                                     (df_menu_items['description'].str.contains('pizza', case=False, na=False))].copy()
    
    # Ensure price is numeric and positive
    pizza_menu_items['price'] = pd.to_numeric(pizza_menu_items['price'], errors='coerce')
    pizza_menu_items.dropna(subset=['price'], inplace=True)
    pizza_menu_items = pizza_menu_items[pizza_menu_items['price'] > 0]

    if not pizza_menu_items.empty:
        os.makedirs(output_dir, exist_ok=True) # Ensure output directory exists
        pizza_menu_items.to_csv(output_csv_path, index=False, encoding='utf-8')
        print(f"Successfully exported {len(pizza_menu_items)} pizza menu items to {output_csv_path}")
    else:
        print("No pizza menu items found to export from combined platforms.")

if __name__ == '__main__':
    export_all_pizza_menu_items_combined(COMBINED_MENU_ITEMS_CSV, OUTPUT_CSV_PATH)
