import pandas as pd
import os

def get_top_pizza_restaurants_combined(combined_restaurants_csv, combined_menu_items_csv, limit=10):
    """
    Retrieves the top N pizza restaurants from the combined dataset based on ratings.
    Normalizes ratings to a common scale if necessary (though the current consolidation
    aims for direct comparison where possible).
    """
    print("Identifying top pizza restaurants for combined platforms...")
    df_restaurants = pd.read_csv(combined_restaurants_csv)
    df_menu_items = pd.read_csv(combined_menu_items_csv)

    # Filter menu items for pizza
    pizza_menu_items = df_menu_items[(df_menu_items['menu_item_name'].str.contains('pizza', case=False, na=False)) |
                                     (df_menu_items['description'].str.contains('pizza', case=False, na=False))]
    
    # Get unique restaurant IDs that offer pizza
    pizza_restaurant_ids = pizza_menu_items['restaurant_id_platform_unique'].unique()

    # Filter restaurants DataFrame to include only those offering pizza
    pizza_restaurants_df = df_restaurants[df_restaurants['restaurant_id_platform_unique'].isin(pizza_restaurant_ids)].copy()

    # Ensure ratings are numeric
    pizza_restaurants_df['rating'] = pd.to_numeric(pizza_restaurants_df['rating'], errors='coerce')
    pizza_restaurants_df['review_count'] = pd.to_numeric(pizza_restaurants_df['review_count'], errors='coerce')

    # Drop restaurants with missing rating or review count (or if they are 0/NaN)
    pizza_restaurants_df.dropna(subset=['rating', 'review_count'], inplace=True)
    pizza_restaurants_df = pizza_restaurants_df[pizza_restaurants_df['review_count'] > 0]
    
    # Sort by rating (descending) then review count (descending)
    top_restaurants = pizza_restaurants_df.sort_values(by=['rating', 'review_count'], ascending=[False, False]).head(limit)

    return top_restaurants[['restaurant_name', 'platform', 'rating', 'review_count']].values.tolist()

if __name__ == '__main__':
    combined_restaurants_csv = 'analysis/combined/all_restaurants.csv'
    combined_menu_items_csv = 'analysis/combined/all_menu_items.csv'
    top_10_pizza = get_top_pizza_restaurants_combined(combined_restaurants_csv, combined_menu_items_csv)

    print("\nTop 10 Pizza Restaurants (by Rating - Combined Platforms):")
    for i, row in enumerate(top_10_pizza, 1):
        print(f"{i}. Restaurant: {row[0]} (Platform: {row[1]}, Rating: {row[2]}, Reviews: {row[3]})")
