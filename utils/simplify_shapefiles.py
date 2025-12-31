import geopandas as gpd

shp_name = '../shapefiles/Belgium-4-Digit-Postcodes-2020.shp'

gdf = gpd.read_file(shp_name)

gdf_precise = gdf.copy()
gdf_precise.geometry = gdf_precise.geometry.set_precision(0.001)

gdf_simplified = gdf_precise.copy()
gdf_simplified.geometry = gdf_simplified.geometry.simplify(
    tolerance=0.001,
    preserve_topology=True
)

gdf_simplified.to_file("../shapefiles/belgium_map_simplified.shp", driver="ESRI Shapefile")

print('Job finished')
################################################

