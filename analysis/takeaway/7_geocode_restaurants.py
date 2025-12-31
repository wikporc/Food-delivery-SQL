import sqlite3
import pandas as pd
import requests
import time
import os
import json
from tqdm import tqdm

OUTPUT_CSV = 'analysis/takeaway/restaurant_postal_codes.csv' # Output file
CHECKPOINT_BATCH_SIZE = 10 # How many restaurants to geocode before saving a checkpoint


def get_postal_code_from_nominatim(lon, lat):
    """
    Reverse geocode coordinates to a postal code using Nominatim API.
    """
    if pd.isna(lon) or pd.isna(lat) or (lon == 0 and lat == 0):
        return None
    
    url = f"https://nominatim.openstreetmap.org/reverse?format=json&lat={lat}&lon={lon}"
    headers = {
        'User-Agent': 'Chrome/143.0.0.0'
    }
    try:
        response = requests.get(url, headers=headers)
        response.raise_for_status()
        data = response.json()
        time.sleep(1) # To respect Nominatim's usage policy (max 1 req/sec)
        if 'address' in data and 'postcode' in data['address']:
            return data['address']['postcode']
    except requests.exceptions.RequestException as e:
        print(f"Error geocoding ({lon}, {lat}): {e}")
    
    return None

def geocode_restaurants_with_checkpointing(db_path):
    conn = sqlite3.connect(db_path)
    restaurants_db_df = pd.read_sql_query("SELECT primarySlug, longitude, latitude FROM restaurants", conn)
    conn.close()

    print(f"Total restaurants in database: {len(restaurants_db_df)}")

    # Initialize restaurants_df_full which will hold all data including geocoded results
    restaurants_df_full = restaurants_db_df.copy()
    restaurants_df_full['postalCode'] = None # Add postalCode column, initially all None

    # Load existing geocoded data (checkpoint) if available
    if os.path.exists(OUTPUT_CSV):
        geocoded_so_far_df = pd.read_csv(OUTPUT_CSV)
        print(f"Loaded {len(geocoded_so_far_df)} previously geocoded restaurants from checkpoint.")
        
        # Update postalCode column in restaurants_df_full with previously geocoded values
        restaurants_df_full = pd.merge(restaurants_df_full, geocoded_so_far_df[['primarySlug', 'postalCode']],
                                       on='primarySlug', how='left', suffixes=('', '_prev'))
        
        # Prioritize checkpoint postalCode
        restaurants_df_full['postalCode'] = restaurants_df_full['postalCode_prev'].fillna(restaurants_df_full['postalCode'])
        restaurants_df_full.drop(columns=['postalCode_prev'], inplace=True)
        
    # Identify restaurants that still need geocoding (those with NaN in postalCode)
    restaurants_to_process = restaurants_df_full[restaurants_df_full['postalCode'].isna()].copy()
    
    if restaurants_to_process.empty:
        print("All restaurants already geocoded.")
        restaurants_df_full.to_csv(OUTPUT_CSV, index=False)
        return

    print(f"Starting geocoding for {len(restaurants_to_process)} remaining restaurants with checkpointing...")
    
    # Ensure longitude and latitude are numeric
    restaurants_to_process['longitude'] = pd.to_numeric(restaurants_to_process['longitude'], errors='coerce')
    restaurants_to_process['latitude'] = pd.to_numeric(restaurants_to_process['latitude'], errors='coerce')
    restaurants_to_process.dropna(subset=['longitude', 'latitude'], inplace=True)


    tqdm.pandas() # Enable tqdm for pandas apply
    
    processed_count = 0
    total_to_process = len(restaurants_to_process)

    # Process in chunks
    for i in tqdm(range(0, total_to_process, CHECKPOINT_BATCH_SIZE), desc="Overall Geocoding Progress"):
        batch = restaurants_to_process.iloc[i : i + CHECKPOINT_BATCH_SIZE].copy()
        
        batch['new_postalCode'] = batch.progress_apply(
            lambda row: get_postal_code_from_nominatim(row['longitude'], row['latitude']),
            axis=1
        )
        
        # Update the full DataFrame with results from this batch
        for _, row in batch.iterrows():
            if pd.notna(row['new_postalCode']):
                restaurants_df_full.loc[restaurants_df_full['primarySlug'] == row['primarySlug'], 'postalCode'] = row['new_postalCode']
            # If new_postalCode is NaN, it means geocoding failed for this restaurant in this run.
            # We don't overwrite any existing postalCode (which would be NaN if not previously geocoded)
            # but leave it as None/NaN in restaurants_df_full for a possible retry in a future run.

        # Save checkpoint to CSV
        os.makedirs(os.path.dirname(OUTPUT_CSV), exist_ok=True)
        restaurants_df_full.to_csv(OUTPUT_CSV, index=False)
        processed_count += len(batch)
        # print(f"Checkpoint saved. Processed {processed_count}/{total_to_process} restaurants.") # Removed for cleaner output

    print(f"Final geocoding complete. Results saved to {OUTPUT_CSV}")

if __name__ == '__main__':
    db_path = 'databases/takeaway.db'
    geocode_restaurants_with_checkpointing(db_path)
