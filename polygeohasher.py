#!/usr/bin/python
import geohash
from polygon_geohasher.polygon_geohasher import polygon_to_geohashes, geohashes_to_polygon
from shapely import *
import pandas as pd
import geopandas as gpd

def create_geohash_list(gdf, geohash_level,inner=False):
    gdf=gdf.copy()
    gdf['geohash_list'] = gdf['geometry'].apply(lambda x: list(polygon_to_geohashes(x, geohash_level,inner)))
    gdf = gdf.drop("geometry",axis = 1)
    return gdf

def polygon_geohash_level(gdf, largest_gh_size, smallest_gh_size, gh_input_level ):
    gdf= gdf.copy()
    gdf['opitimized_geohash_list'] = gdf['geohash_list'].apply(lambda x : __util_geohash_optimizer(x,largest_gh_size, smallest_gh_size, gh_input_level,10,True))
    data = gdf.drop('geohash_list',axis=1).copy()
    df = pd.DataFrame(data)
    df = df.explode('opitimized_geohash_list')
    df.drop_duplicates('opitimized_geohash_list',inplace=True)
    return df

def geohashes_to_geometry(df):
    df = df.copy()
    df['geometry'] = df['opitimized_geohash_list'].apply(lambda x : geohashes_to_polygon([str(x)]))
    gdf = gpd.GeoDataFrame(df, geometry=df["geometry"])
    return gdf

def optimization_summary(initial_gdf, final_gdf):
    print("-"*50)
    print("\t\tOPTIMIZATION SUMMARY")
    print("-"*50)
    initial_count = sum([len(i) for i in initial_gdf["geohash_list"]])
    print("Total Counts of Initial Geohashes : ",initial_count)
    final_count = len(final_gdf)
    print("Total Counts of Final Geohashes   : ",final_count)
    print("Percent of optimization           : ",round(((initial_count - final_count)/initial_count)*100,2),"%")
    print("-"*50)

# Recursive optimization of the geohash set
def __util_geohash_optimizer(geohashes, largest_gh_size, smallest_gh_size, gh_input_level, percent_error=10,forced_gh_upscale = False):
    base32 = ['0', '1', '2', '3', '4', '5', '6', '7', '8', '9', 'b', 'c', 'd', 'e', 'f', 'g', 'h', 'j', 'k', 'm',
            'n', 'p', 'q', 'r', 's', 't', 'u', 'v', 'w', 'x', 'y', 'z']
    geohashes = set(geohashes)
    geohash_processed_check = set()
    processed_geohash_set = set()
    flag = True
    # Input size less than 32
    if len(geohashes) == 0:
        return False
    len_desired_reached = False
    no_of_cycle = 0
    if smallest_gh_size < gh_input_level:
        cutoff = (gh_input_level - smallest_gh_size) + (smallest_gh_size - largest_gh_size)
    else:
        cutoff = smallest_gh_size-largest_gh_size
    while flag == True:
        processed_geohash_set.clear()
        geohash_processed_check.clear()
        geohashes = set(geohashes)
        len_desired = largest_gh_size
        for geohash in geohashes:
            geohash_length = len(geohash)
            if geohash_length == len_desired or len_desired_reached == True:
                len_desired_reached = True
            else:
                len_desired_reached = False
            # Compress only if geohash length is greater than the min level
            if geohash_length >= largest_gh_size:
                # Get geohash to generate combinations for
                geohash_1up = geohash[:-1]
                # Proceed only if not already processed
                if (geohash_1up not in geohash_processed_check) and (geohash not in geohash_processed_check):
                    # Generate combinations
                    combinations = set([geohash_1up + i for i in base32])
                    # If all generated combinations exist in the input set
                    intersect = combinations.intersection(geohashes)
                    if combinations.issubset(geohashes) or (len(intersect) >= 32 * (1 - percent_error/100) and no_of_cycle < 1 ):
                        # Add part to temporary output
                        processed_geohash_set.add(geohash_1up)
                        # Add part to deleted geohash set
                        geohash_processed_check.add(geohash_1up)
                    # Else add the geohash to the temp out and deleted set
                    else:
                        geohash_processed_check.add(geohash)
                        # Forced compression if geohash length is greater than max level after combination check failure
                        if geohash_length >= smallest_gh_size and forced_gh_upscale == True:
                            processed_geohash_set.add(geohash[:smallest_gh_size])
                        else:
                            processed_geohash_set.add(geohash)
        no_of_cycle = no_of_cycle+1
        if len_desired_reached == True or no_of_cycle >= (cutoff):
            flag = False
        geohashes.clear()
            # Temp output moved to the primary geohash set
        geohashes = geohashes.union(processed_geohash_set)
    geohashes = list(set(geohashes))  
    return geohashes