#!/usr/bin/python

# the purpose is to pass a geodataframe and convert it to a list of geohash for a given range of geohash levels
# with a certain degree of approximation to convert a finer level of geohash to coarser level (based on the % of lower GH member present in the data)


#dependies 
import geohash
from polygon_geohasher.polygon_geohasher import polygon_to_geohashes, geohashes_to_polygon
from shapely import *
import pandas as pd
import geopandas as gpd

gdf = gpd.read_file("/data/sample.geojson")

def poly_to_geohash(p,geohash_level):
    lst = list(polygon_to_geohashes(p, geohash_level,False))
    #lst = '~'.join(lst)
    return lst

gdf['geohash_list'] = gdf['geometry'].apply(poly_to_geohash)

gdf = gdf.drop("geometry",axis = 1)

# Recursive optimization of the geohash set
def geohash_level_optimizer(geohashes, largest_gh_size, smallest_gh_size, gh_input_level, percent_error=10,forced_gh_upscale = False):
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
        #     print(gehash,geohash_length)
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
        #                 print(final_geohashes)
                        # Add part to deleted geohash set
                        geohash_processed_check.add(geohash_1up)
        #                 print(deletegh)
                    # Else add the geohash to the temp out and deleted set
                    else:
                        geohash_processed_check.add(geohash)
                        # Forced compression if geohash length is greater than max level after combination check failure
                        if geohash_length >= smallest_gh_size and forced_gh_upscale == True:
                            processed_geohash_set.add(geohash[:smallest_gh_size])
                        else:
                            processed_geohash_set.add(geohash)
    #                 print(len(final_geohashes))
        geohash_set_size = len(processed_geohash_set)
        print('no. of geohashes final:',geohash_set_size,'min gh level required',len_desired,'cutoff',cutoff)
        no_of_cycle = no_of_cycle+1
        if len_desired_reached == True or no_of_cycle >= (cutoff):
            flag = False
        geohashes.clear()
            # Temp output moved to the primary geohash set
        geohashes = geohashes.union(processed_geohash_set)
    geohashes = list(set(geohashes))    
    return geohashes

gdf['opitimed_geohash_list'] = gdf['geohash_list'].apply(lambda x : geohash_level_optimizer(x,5,6,7,10,True))

data = gdf.drop('geohash_list',axis=1).copy()

data = pd.DataFrame(data)

data = data.explode('opitimed_geohash_list')

data.drop_duplicates('opitimed_geohash_list',inplace=True)

def gh_to_poly(gh):
    return geohashes_to_polygon([str(gh)])

data['geometry'] = data['opitimed_geohash_list'].apply(gh_to_poly)
gdf_final = gpd.GeoDataFrame(
    data, geometry=data['geometry'])
gdf_final.plot()

gdf_final.to_file("/Users/rohitsingh/Documents/Rohit Singh/random data/test_56.geojson",driver='GeoJSON')
