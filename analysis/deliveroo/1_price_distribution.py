import sqlite3
import pandas as pd
import matplotlib.pyplot as plt
import os

def analyze_price_distribution_deliveroo(db_path, output_dir='analysis/deliveroo'):
    """
    Analyzes the price distribution of menu items from the deliveroo.db database.

    Args:
        db_path (str): The path to the SQLite database file.
        output_dir (str): The directory to save the histogram image.
    """
    conn = sqlite3.connect(db_path)

    query = "SELECT price FROM menu_items"
    df = pd.read_sql_query(query, conn)

    conn.close()

    df['price'] = pd.to_numeric(df['price'], errors='coerce')
    df.dropna(subset=['price'], inplace=True)

    plt.figure(figsize=(10, 6))
    plt.hist(df['price'], bins=3350, edgecolor='black')
    plt.xlim(0,120)
    plt.title('Price Distribution of Menu Items (Deliveroo)')
    plt.xlabel('Price (in EUR)')
    plt.ylabel('Number of Items')
    plt.grid(axis='y', alpha=0.75)

    os.makedirs(output_dir, exist_ok=True) # Ensure output directory exists
    plt.savefig(os.path.join(output_dir, 'price_distribution.png'))
    plt.close()

    print("Price Distribution Summary (Deliveroo):")
    print(df['price'].describe())

if __name__ == '__main__':
    db_path = 'databases/deliveroo.db'
    analyze_price_distribution_deliveroo(db_path)
