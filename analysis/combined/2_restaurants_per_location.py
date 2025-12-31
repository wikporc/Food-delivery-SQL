import pandas as pd
import matplotlib.pyplot as plt
import os

def analyze_restaurants_per_location_combined(combined_restaurants_csv, output_dir='analysis/combined'):
    """
    Analyzes how restaurants are distributed across different standardized cities for combined platforms.

    Args:
        combined_restaurants_csv (str): The path to the combined restaurants CSV file.
        output_dir (str): The directory to save the generated plots.
    """
    print("Analyzing restaurant distribution for combined platforms...")
    df_restaurants = pd.read_csv(combined_restaurants_csv)
    
    df_restaurants.dropna(subset=['standardized_city'], inplace=True)

    # Group by the standardized city
    df_city = df_restaurants.groupby('standardized_city').agg(
        restaurant_count=('restaurant_id_platform_unique', 'nunique') # Use unique ID to count unique restaurants
    ).reset_index()
    df_city.rename(columns={'standardized_city': 'city'}, inplace=True)
    df_city.sort_values(by='restaurant_count', ascending=False, inplace=True)

    if df_city.empty:
        print("\nNo cities found after standardization and grouping. Cannot generate report.")
        return

    total_for_percentage = df_city['restaurant_count'].sum()
    df_city['percentage'] = (df_city['restaurant_count'] / total_for_percentage) * 100

    os.makedirs(output_dir, exist_ok=True) # Ensure output directory exists

    # --- Visualization 1: Top 20 cities by number of restaurants ---
    top_20 = df_city.head(20)
    plt.figure(figsize=(12, 8))
    plt.barh(top_20['city'], top_20['restaurant_count'], color='skyblue')
    plt.xlabel('Number of Unique Restaurants')
    plt.ylabel('City')
    plt.title('Top 20 Cities by Number of Unique Restaurants (Combined Platforms)')
    plt.gca().invert_yaxis()
    plt.tight_layout()
    plt.savefig(os.path.join(output_dir, 'restaurants_per_location.png'))
    plt.close()

    # --- Visualization 2: Concentration of restaurants ---
    top_10_pie = df_city.head(10).copy()
    other_percentage = df_city['percentage'][10:].sum()
    if other_percentage > 0:
        top_10_pie.loc[len(top_10_pie)] = {'city': 'Other', 'restaurant_count': 0, 'percentage': other_percentage}


    plt.figure(figsize=(10, 10))
    plt.pie(top_10_pie['percentage'], labels=top_10_pie['city'], autopct='%1.1f%%', startangle=140)
    plt.title('Restaurant Concentration in Top 10 Cities (Combined Platforms)')
    plt.axis('equal')
    plt.savefig(os.path.join(output_dir, 'restaurants_concentration.png'))
    plt.close()

    print("\nTop 10 cities with most unique restaurants (Combined Platforms):")
    print(df_city.head(10).to_markdown(index=False))

    print(f"\nNote: Percentages are relative to the total number of unique restaurants in the dataset.")

if __name__ == '__main__':
    combined_restaurants_csv = 'analysis/combined/all_restaurants.csv'
    analyze_restaurants_per_location_combined(combined_restaurants_csv)
