import sqlite3
import re
import math
import matplotlib.pyplot as plt
import pandas as pd
import os

def analyze_pizza_prices_deliveroo(db_path, output_dir='analysis/deliveroo'):
    """
    Analyzes the price per square centimeter of pizzas from the deliveroo.db database,
    handling both circular and rectangular pizzas, and generates a histogram.

    Args:
        db_path (str): The path to the SQLite database file.
        output_dir (str): The directory to save the histogram image.

    Returns:
        list: A sorted list of tuples, where each tuple contains:
              (restaurant_name, pizza_name, price, size_str, area, price_per_sq_cm)
    """
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()

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
            (mi.name LIKE '%pizza%')
            AND (mi.description LIKE '%cm%' OR mi.name LIKE '%cm%')
            AND mi.price > 0; -- Filter out non-positive prices
    """
    cursor.execute(query)
    pizzas = cursor.fetchall()
    conn.close()

    pizza_analysis = []
    rect_regex = re.compile(r'(\d+)\s*x\s*(\d+)\s*cm')
    circ_regex = re.compile(r'(\d+)\s*cm')

    for restaurant_name, pizza_name, price_str, description in pizzas:
        try:
            price = float(price_str)
        except (ValueError, TypeError):
            continue # Skip this item if price cannot be converted to float
        # Deliveroo prices are already in euros, no conversion needed
        
        search_text = f"{pizza_name} {description}"
        
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

        if area > 0 and price > 0:
            price_per_sq_cm = price / area
            pizza_analysis.append((restaurant_name, pizza_name, price, size_str, area, price_per_sq_cm))

    pizza_analysis.sort(key=lambda x: x[5])

    os.makedirs(output_dir, exist_ok=True) # Ensure output directory exists

    # Generate and save histogram
    prices_per_cm2 = [item[5] for item in pizza_analysis]
    if prices_per_cm2:
        plt.figure(figsize=(10, 6))
        # Filter out extreme outliers for better visualization in histogram if needed
        # Q1, Q3 = np.percentile(prices_per_cm2, [25, 75])
        # IQR = Q3 - Q1
        # upper_bound = Q3 + 1.5 * IQR
        # filtered_prices_per_cm2 = [p for p in prices_per_cm2 if p < upper_bound]
        plt.hist(prices_per_cm2, bins=150, edgecolor='black', range=(0, 0.06)) # Set a reasonable range
        plt.title('Distribution of Pizza Price per cm² (Deliveroo)')
        plt.xlabel('Price per cm² (€)')
        plt.ylabel('Number of Pizzas')
        plt.grid(axis='y', alpha=0.75)
        plt.savefig(os.path.join(output_dir, 'price_per_cm2_distribution.png'))
        plt.close()
    else:
        print(f"No valid pizza data with size information for histogram generation in {db_path}.")


    return pizza_analysis

if __name__ == '__main__':
    db_path = 'databases/deliveroo.db'
    best_value_pizzas = analyze_pizza_prices_deliveroo(db_path)

    if best_value_pizzas:
        print("Top 10 Best Value Pizzas (Price per cm² - Deliveroo):")
        for i, pizza in enumerate(best_value_pizzas[:10], 1):
            print(f"{i}. Restaurant: {pizza[0]}")
            print(f"   Pizza: {pizza[1]}")
            print(f"   Price: €{pizza[2]:.2f}, Size: {pizza[3]}, Surface: {pizza[4]:.2f}cm²")
            print(f"   Price per cm²: €{pizza[5]:.4f}")
            print("-" * 20)
    else:
        print("No best value pizzas found with size information.")
