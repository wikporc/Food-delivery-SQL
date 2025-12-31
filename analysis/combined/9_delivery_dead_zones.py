import pandas as pd
import geopandas as gpd
import matplotlib.pyplot as plt
import os

# Paths
COMBINED_RESTAURANTS_CSV = 'analysis/combined/all_restaurants.csv'
SHAPEFILE_PATH = 'shapefiles/Belgium-4-Digit-Postcodes-2020.shp'
OUTPUT_MAP_PATH = 'analysis/combined/delivery_dead_zones_map.png'

def generate_dead_zones_map_combined(combined_restaurants_csv, output_dir='analysis/combined'):
    """
    Generates a choropleth map highlighting delivery "dead zones" (areas with low/no restaurant coverage)
    for combined platforms based on postal codes.
    """
    print("Generating Delivery Dead Zones Map for Combined Platforms...")

    # Load combined restaurants data
    df_restaurants_geo = pd.read_csv(combined_restaurants_csv)
    df_restaurants_geo.dropna(subset=['postalCode'], inplace=True)
    df_restaurants_geo['postalCode'] = pd.to_numeric(df_restaurants_geo['postalCode'], errors='coerce')
    df_restaurants_geo.dropna(subset=['postalCode'], inplace=True) # Explicitly drop NaNs here
    df_restaurants_geo['postalCode'] = df_restaurants_geo['postalCode'].astype(int)

    # Count unique restaurants per postal code
    restaurant_counts_by_postal = df_restaurants_geo.groupby('postalCode')['restaurant_id_platform_unique'].nunique().reset_index()
    restaurant_counts_by_postal.rename(columns={'restaurant_id_platform_unique': 'restaurant_count'}, inplace=True)

    # Load postal code boundaries shapefile
    if not os.path.exists(SHAPEFILE_PATH):
        print(f"Error: Shapefile not found at {SHAPEFILE_PATH}.")
        return

    belgium_map = gpd.read_file(SHAPEFILE_PATH)
    belgium_map['nouveau_PO'] = pd.to_numeric(belgium_map['nouveau_PO'], errors='coerce').astype(int)

    # Merge the GeoDataFrame with the restaurant count data
    merged_map_data = belgium_map.set_index('nouveau_PO').join(restaurant_counts_by_postal.set_index('postalCode'))
    
    # Fill NaN values (postal codes with no restaurants) with 0
    merged_map_data['restaurant_count'] = merged_map_data['restaurant_count'].fillna(0)

    # Create the plot
    fig, ax = plt.subplots(1, 1, figsize=(15, 15))
    
    # Plot postal code areas by restaurant count
    merged_map_data.plot(column='restaurant_count', 
                         cmap='YlOrRd', # Yellow-Orange-Red colormap, lighter for less restaurants
                         linewidth=0.8, 
                         ax=ax, 
                         edgecolor='0.8',
                         legend=True, 
                         legend_kwds={'label': "Number of Restaurants", 'orientation': "horizontal"},
                         missing_kwds={"color": "#cccccc", "edgecolor": "red", "hatch": "///", "label": "No Data (e.g., outside Belgium or missing postal code)"}
                        )

    # Highlight "dead zones" (areas with 0 restaurants)
    dead_zones = merged_map_data[merged_map_data['restaurant_count'] == 0]
    dead_zones.plot(ax=ax, color='black', hatch='..', edgecolor='black', alpha=0.7, label='Dead Zone (0 Restaurants)')
    
    ax.set_title('Combined Platforms: Restaurant Coverage by Postal Code (Delivery Dead Zones)', fontdict={'fontsize': '18', 'fontweight': '3'})
    ax.set_axis_off()
        
    os.makedirs(output_dir, exist_ok=True)
    plt.savefig(OUTPUT_MAP_PATH, dpi=300)
    plt.close()

    print(f"Delivery dead zones map saved to: {OUTPUT_MAP_PATH}")

if __name__ == '__main__':
    generate_dead_zones_map_combined(COMBINED_RESTAURANTS_CSV)
