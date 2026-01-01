import pandas as pd
import matplotlib.pyplot as plt
import os

def analyze_price_distribution_combined(combined_menu_items_csv, output_dir='analysis/combined'):
    """
    Analyzes the price distribution of menu items from the combined dataset.

    Args:
        combined_menu_items_csv (str): The path to the combined menu items CSV file.
        output_dir (str): The directory to save the histogram image.
    """
    print("Analyzing price distribution for combined platforms...")
    df = pd.read_csv(combined_menu_items_csv)

    # Data cleaning: convert price to numeric, coercing errors
    df['price'] = pd.to_numeric(df['price'], errors='coerce')
    df.dropna(subset=['price'], inplace=True)

    # Filter out prices that are less than or equal to 0, as they indicate data quality issues or non-saleable items
    df = df[df['price'] > 0]

    # Create the histogram
    plt.figure(figsize=(10, 6))
    plt.hist(df['price'], bins=1000, edgecolor='black')
    plt.xlim(0,50)
    plt.title('Price Distribution of Menu Items (Combined Platforms)')
    plt.xlabel('Price (in EUR)')
    plt.ylabel('Number of Items')
    plt.grid(axis='y', alpha=0.75)

    os.makedirs(output_dir, exist_ok=True) # Ensure output directory exists
    plt.savefig(os.path.join(output_dir, 'price_distribution.png'))
    plt.close()

    print("Price Distribution Summary (Combined Platforms):")
    print(df['price'].describe())

if __name__ == '__main__':
    combined_menu_items_csv = 'analysis/combined/all_menu_items.csv'
    analyze_price_distribution_combined(combined_menu_items_csv)
