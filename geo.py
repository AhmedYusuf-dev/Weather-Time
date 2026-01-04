import geopandas as gpd
gdf = gpd.read_file("ne_10m_populated_places.shp")
gdf[['NAME','ADM0NAME','LATITUDE','LONGITUDE','POP_MAX']].to_csv("natural_earth_cities.csv", index=False)
