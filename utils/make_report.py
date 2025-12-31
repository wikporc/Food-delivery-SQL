import pandas as pd
import matplotlib.pyplot as plt
import geopandas as gpd
import os
import numpy as np

from tabulate import tabulate

from service_functions import get_province_by_postcode, get_region_by_postcode  

################################################

### Read data ###

# Big dataset
filename = '../data/cleaned/cleaned_dataset_v3.csv'
df = pd.read_csv(filename,delimiter=',')

col = 'url'  # Drop the column Url because it needn't for analysis
if col in df.columns:
    df.drop(columns=[col], inplace=True)

# Table of postal codes
csv_name = '../shapefiles/postal_codes.csv'
df_post = pd.read_csv(csv_name, sep=';' )
df_post['postal_code'] = df_post['postal_code'].astype(int)

##################################################################

### Add province and mun name to the dataset ###

df = df.merge(   df_post[['postal_code', 'mun_name']],
    on='postal_code',
    how='left'
)

df[['province_num', 'province_name']] = (
    df['postal_code']
    .apply(get_province_by_postcode)
    .apply(pd.Series)
)

assert df['mun_name'].isna().sum() == 0 
assert df['province_name'].isna().sum() == 0

df[['region_num', 'region_name']] = (
    df['postal_code']
    .apply(get_region_by_postcode)
    .apply(pd.Series)
)

##################################################################

### Group by municipality ###

df_count = df.groupby('postal_code').size().reset_index(name='count')

median_price = df.groupby('postal_code')['price'].median().reset_index(name='median_total_price')
mean_price = df.groupby('postal_code')['price'].mean().reset_index(name='mean_total_price')

df['price_per_m2'] = df['price'] / df['area']

df_price_per_m2 = df.groupby('postal_code', as_index=False)['price_per_m2'].median()
df_price_per_m2.rename(columns={'price_per_m2': 'median_price_per_m2'}, inplace=True)

df_price_per_m2_average = df.groupby('postal_code', as_index=False)['price_per_m2'].mean()
df_price_per_m2_average.rename(columns={'price_per_m2': 'mean_price_per_m2'}, inplace=True)

percent_luxurious = (
    df.groupby('postal_code')['is_luxurious']
    .mean()  # mean - 
    .mul(100)  # convert to percents
    .astype(int)
    .reset_index(name='percent_luxurious')
)


df_summary = (df_count
              .merge(median_price, on='postal_code', how='left')
              .merge(mean_price, on='postal_code', how='left')
              .merge(df_price_per_m2, on='postal_code', how='left')
              .merge(df_price_per_m2_average, on='postal_code', how='left')
              .merge(percent_luxurious, on='postal_code', how='left')
              )

#print( df_summary.shape )

assert df_summary.isna().sum().sum() == 0

# Round to int
float_cols = df_summary.select_dtypes(include='float').columns
df_summary[float_cols] = df_summary[float_cols].astype('int')

# Merge with names of municip.

df_summary = df_summary.merge(   df_post[['postal_code', 'mun_name']],
    on='postal_code',
    how='left'
)

province_map = df[['postal_code','province_num', 'province_name']].drop_duplicates() 
df_summary = df_summary.merge(province_map, on='postal_code', how='left')

regions_map = df[['postal_code','region_num', 'region_name']].drop_duplicates() 
df_summary = df_summary.merge(regions_map, on='postal_code', how='left')

##################################################################

### Group by provinces ###

df_count = df.groupby('province_num').size().reset_index(name='count')

median_price = df.groupby('province_num')['price'].median().reset_index(name='median_total_price')
mean_price = df.groupby('province_num')['price'].mean().reset_index(name='mean_total_price')

df['price_per_m2'] = df['price'] / df['area']

df_price_per_m2 = df.groupby('province_num', as_index=False)['price_per_m2'].median()
df_price_per_m2.rename(columns={'price_per_m2': 'median_price_per_m2'}, inplace=True)

df_price_per_m2_average = df.groupby('province_num', as_index=False)['price_per_m2'].mean()
df_price_per_m2_average.rename(columns={'price_per_m2': 'mean_price_per_m2'}, inplace=True)

percent_luxurious = (
    df.groupby('province_num')['is_luxurious']
    .mean()  # mean - 
    .mul(100)  # convert to percents
    .astype(int)
    .reset_index(name='percent_luxurious')
)

df_summary_prov = (df_count
              .merge(median_price, on='province_num', how='left')
              .merge(mean_price, on='province_num', how='left')
              .merge(df_price_per_m2, on='province_num', how='left')
              .merge(df_price_per_m2_average, on='province_num', how='left')
              .merge(percent_luxurious, on='province_num', how='left')
              )

assert df_summary_prov.isna().sum().sum() == 0

# Round to int
float_cols = df_summary_prov.select_dtypes(include='float').columns
df_summary_prov[float_cols] = df_summary_prov[float_cols].astype('int')

# Merge with names of regions

province_map = df[['province_num', 'province_name']].drop_duplicates() 

df_summary_prov = df_summary_prov.merge(province_map, on='province_num', how='left')

#print( df_summary_prov.shape )

##################################################################

### Save results to files ###

#results_dir = './'
results_dir = '../map_visualization_results/'

outname = 'summary_by_municip.csv'
filepath = os.path.join(results_dir, outname)

df_summary.to_csv(filepath, sep=';', index=False, encoding='utf-8')

outname = 'summary_by_provinces.csv'
filepath = os.path.join(results_dir, outname)

df_summary_prov.to_csv(filepath, sep=';', index=False, encoding='utf-8')

##################################################################

### Show results in a console ###

#print(df_summary_prov.info() )

df_summary_prov.sort_values(by='median_total_price', inplace=True, ascending=True)

if(0):

    print( tabulate(df_summary_prov[['province_name',
                                     'median_total_price',
                                     'mean_total_price',
                                     'percent_luxurious',
                                     'median_price_per_m2',
                                     'mean_price_per_m2'
                                     
                                    ]],
                    headers='keys', 
                    tablefmt='psql', 
                    showindex=False))

##################################################################

print('The job have done')

