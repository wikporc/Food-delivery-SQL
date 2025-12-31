import geopandas as gpd
import pandas as pd

################################################

def get_province(pcode_i: int):
    """
    Convert belgium postal code to the name of province (and abstract number)
    """

    try:
        pcode = int(pcode_i)  
    except ValueError:
        return None, None  

       
    if 1000 <= pcode <= 1299:
        return 10, 'Brussels'
    elif 1300 <= pcode <= 1499:
        return 1,'Walloon Brabant'
    elif 1500 <= pcode <= 1999 or 3000 <= pcode <= 3499:
        return 3, 'Flemish Brabant'
    elif 2000 <= pcode <= 2999:
        return 2, 'Antwerp'
    elif 3500 <= pcode <= 3999:
        return 9, 'Limburg'
    elif 4000 <= pcode <= 4999:
        return 4, 'Liege'
    elif 5000 <= pcode <= 5999:
        return 5, 'Namur'
    elif 6000 <= pcode <= 6599 or 7000 <= pcode <= 7999:
        return 7, 'Hainaut'
    elif 6600 <= pcode <= 6999:
        return 6, 'Luxembourg'
    elif 8000 <= pcode <= 8999:
        return 8, 'West Flanders'
    elif 9000 <= pcode <= 9999:
        return 9, 'East Flanders'
    else:
        print('Incorrect code:',pcode)
        return 0,'Incorrect postal code'


################################################


shp_name = '../shapefiles/Belgium-4-Digit-Postcodes-2020.shp'

gdf = gpd.read_file(shp_name)

# Column for province's names
gdf[['prov_num', 'prov_name']] = gdf['nouveau_PO'].apply(
    lambda x: pd.Series(get_province(x))  # pd.Series - tuple to dataset's columns
)

# group by provinces and join geometry
gdf_provinces = gdf.dissolve(
    by=['prov_num', 'prov_name'], 
    as_index=False
)

# save shp-file
gdf_provinces.to_file("provinces.shp")

print('Job finished')
################################################

