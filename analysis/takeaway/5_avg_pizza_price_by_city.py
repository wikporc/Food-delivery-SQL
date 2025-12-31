import sqlite3
import re
import math
import pandas as pd
import os

def analyze_avg_pizza_price_by_city(db_path, min_pizza_count=10):
    """
    Analyzes the average price per square centimeter of pizzas by city,
    filtering for cities with a minimum number of pizza offerings.

    Args:
        db_path (str): The path to the SQLite database file.
        min_pizza_count (int): The minimum number of pizzas a city must have to be included.

    Returns:
        pd.DataFrame: A pandas DataFrame with the average price per cm² for each city,
                      sorted by the best value.
    """
    conn = sqlite3.connect(db_path)
    
    query = """
        SELECT
            r.city,
            mi.name,
            mi.price,
            mi.description
        FROM
            menuItems mi
        JOIN
            restaurants r ON mi.primarySlug = r.primarySlug
        WHERE
            (mi.name LIKE '%pizza%')
            AND (mi.description LIKE '%cm%' OR mi.name LIKE '%cm%');
    """
    df = pd.read_sql_query(query, conn)
    conn.close()

    pizza_data = []
    rect_regex = re.compile(r'(\d+)\s*x\s*(\d+)\s*cm')
    circ_regex = re.compile(r'(\d+)\s*cm')

    for index, row in df.iterrows():
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
        
        if area > 0 and row['price'] > 0:
            price_per_sq_cm = row['price'] / area
            pizza_data.append({'city': row['city'], 'price_per_sq_cm': price_per_sq_cm})

    if not pizza_data:
        return pd.DataFrame(columns=['city', 'avg_price_per_sq_cm', 'pizza_count'])

    pizza_df = pd.DataFrame(pizza_data)

    # Group by city and calculate the average price_per_sq_cm and the count of pizzas
    city_analysis = pizza_df.groupby('city').agg(
        avg_price_per_sq_cm=('price_per_sq_cm', 'mean'),
        pizza_count=('price_per_sq_cm', 'size')
    ).reset_index()

    # Filter out cities with fewer than the minimum pizza count (commented out for now)
    
    # city_analysis = city_analysis[city_analysis['pizza_count'] >= min_pizza_count]

    # Sort by average price per square centimeter (best value first)
    city_analysis = city_analysis.sort_values('avg_price_per_sq_cm').reset_index(drop=True)

    return city_analysis

if __name__ == '__main__':
    db_path = 'databases/takeaway.db'
    output_csv_path = 'analysis/takeaway/avg_pizza_price_by_city_all.csv'
    
    all_cities_analysis = analyze_avg_pizza_price_by_city(db_path, min_pizza_count=0) # Pass 0 to effectively remove filter

    print("All Cities with Average Pizza Value (Price per cm²):")
    print(all_cities_analysis.to_string())

    all_cities_analysis.to_csv(output_csv_path, index=False)
    print(f"\nFull city analysis saved to: {output_csv_path}")