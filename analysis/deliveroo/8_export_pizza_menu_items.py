import sqlite3
import pandas as pd
import os

def export_all_pizza_menu_items_deliveroo(db_path, output_csv_path):
    """
    Queries the Deliveroo database for all menu items containing 'pizza' in their name or description
    and exports them to a CSV file. Prices are assumed to be in euros.

    Args:
        db_path (str): Path to the SQLite database.
        output_csv_path (str): Path to save the output CSV file.
    """
    conn = sqlite3.connect(db_path)

    query = """
        SELECT
            r.name AS restaurant_name,
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
        df.to_csv(output_csv_path, index=False, encoding='utf-8')
        print(f"Successfully exported {len(df)} pizza menu items to {output_csv_path}")
    else:
        print("No pizza menu items found to export.")

if __name__ == '__main__':
    db_path = 'databases/deliveroo.db'
    output_csv_path = 'analysis/deliveroo/all_pizza_menu_items.csv'
    export_all_pizza_menu_items_deliveroo(db_path, output_csv_path)
