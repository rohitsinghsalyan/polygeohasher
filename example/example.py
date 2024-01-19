import geopandas as gpd
from polygeohasher import polygeohasher

gdf = gpd.read_file("sample.geojson")
pgh = polygeohasher.Polygeohasher(gdf)

initial_df = pgh.create_geohash_list(6,inner=False)
print(initial_df)

final_df = pgh.geohash_optimizer(initial_df, 5,7, 6) 
print(final_df)

#prints optimization summary
pgh.optimization_summary(initial_df, final_df)

#Convert geohash to geometry
geo_df = pgh.geohashes_to_geometry(final_df)
print(geo_df)