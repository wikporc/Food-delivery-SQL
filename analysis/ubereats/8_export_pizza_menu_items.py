import sqlite3
import pandas as pd
import os

def export_all_pizza_menu_items_ubereats(db_path, output_csv_path):
    """
    Queries the Uber Eats database for all menu items containing 'pizza' in their name or description
    and exports them to a CSV file. Converts prices from cents to euros.

    Args:
        db_path (str): Path to the SQLite database.
        output_csv_path (str): Path to save the output CSV file.
    """
    conn = sqlite3.connect(db_path)

    query = """
        SELECT
            r.title AS restaurant_name,
            mi.name AS menu_item_name,
            mi.price,
            mi.description
        FROM
            menu_items mi
        JOIN
            restaurants r ON mi.restaurant_id = r.id
        WHERE
            mi.name LIKE '%pizza%' OR mi.description LIKE '%pizza%';
    """
    df = pd.read_sql_query(query, conn)
    conn.close()

    if not df.empty:
        # Convert price from cents to euros
        df['price'] = df['price'] / 100.0
        df.to_csv(output_csv_path, index=False, encoding='utf-8')
        print(f"Successfully exported {len(df)} pizza menu items to {output_csv_path}")
    else:
        print("No pizza menu items found to export.")

if __name__ == '__main__':
    db_path = 'databases/ubereats.db'
    output_csv_path = 'analysis/ubereats/all_pizza_menu_items.csv'
    export_all_pizza_menu_items_ubereats(db_path, output_csv_path)
