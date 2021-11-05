#!/usr/bin/python
import geohash
from polygon_geohasher.polygon_geohasher import (
    polygon_to_geohashes,
    geohashes_to_polygon,
)
from shapely import *
import pandas as pd
import geopandas as gpd


def create_geohash_list(gdf, geohash_level, inner=False):
    """Return a list of geohash for each individual geometry polygon
    when supplied with a geo DataFrame and level of precision for geohash.
    The geohash list is added as a list against each geometry."""
    gdf = gdf.copy()
    gdf["geohash_list"] = gdf["geometry"].apply(
        lambda x: list(polygon_to_geohashes(x, geohash_level, inner))
    )
    gdf = gdf.drop("geometry", axis=1)
    return gdf


def geohash_optimizer(
    gdf,
    largest_gh_size,
    smallest_gh_size,
    gh_input_level,
    percentage_error=10,
    forced_gh_upscale=False,
):
    """Return a list of geohash of optimized geohash levels to cover a ceratin area (Polygon).
    Takes a DataFrame as input with target column conisiting of the geohash list, Desired range of geohash levels,
    input level of geohash and optional error of percentage of geohash optimisation and force optimisation. The output is a DataFrame
    with optimized geohashes for each geometry"""
    gdf = gdf.copy()
    gdf["optimized_geohash_list"] = gdf["geohash_list"].apply(
        lambda x: __util_geohash_optimizer(
            x,
            largest_gh_size,
            smallest_gh_size,
            gh_input_level,
            percentage_error,
            forced_gh_upscale,
        )
    )
    data = gdf.drop("geohash_list", axis=1).copy()
    df = pd.DataFrame(data)
    df = df.explode("optimized_geohash_list")
    df.drop_duplicates("optimized_geohash_list", inplace=True)
    return df


def geohashes_to_geometry(df, geohash_column_name):
    """returns a geo DataFrame for the geohashes to visualise them on a map. the user can save it in any of the Popular
    formats like ESRI Shapefile, GeoJSON etc."""
    df = df.copy()
    if type(df[geohash_column_name][0]) == list:
        df = pd.DataFrame(df)
        df = df.explode(geohash_column_name)
    df["geometry"] = df[geohash_column_name].apply(
        lambda x: geohashes_to_polygon([str(x)])
    )
    # df['geometry'] = df['opitimized_geohash_list'].apply(lambda x : geohashes_to_polygon([str(x)]))
    gdf = gpd.GeoDataFrame(df, geometry=df["geometry"])
    return gdf


def optimization_summary(initial_gdf, final_gdf):
    """returns the summary of optimization of number of geohashes to cover an AREA. The user needs to pass the
    two data Frames (Initial Geohash - raw, and optimized one)"""
    print("-" * 50)
    print("\t\tOPTIMIZATION SUMMARY")
    print("-" * 50)
    initial_count = sum([len(i) for i in initial_gdf["geohash_list"]])
    print("Total Counts of Initial Geohashes : ", initial_count)
    final_count = len(final_gdf)
    print("Total Counts of Final Geohashes   : ", final_count)
    print(
        "Percent of optimization           : ",
        round(((initial_count - final_count) / initial_count) * 100, 2),
        "%",
    )
    print("-" * 50)


# Recursive optimization of the geohash set
def __util_geohash_optimizer(
    geohashes,
    largest_gh_size,
    smallest_gh_size,
    gh_input_level,
    percentage_error,
    forced_gh_upscale,
):
    base32 = [
        "0",
        "1",
        "2",
        "3",
        "4",
        "5",
        "6",
        "7",
        "8",
        "9",
        "b",
        "c",
        "d",
        "e",
        "f",
        "g",
        "h",
        "j",
        "k",
        "m",
        "n",
        "p",
        "q",
        "r",
        "s",
        "t",
        "u",
        "v",
        "w",
        "x",
        "y",
        "z",
    ]  # set of hash values to build the geohash
    geohashes = set(geohashes)
    geohash_processed_check = set()
    processed_geohash_set = set()
    flag = True  # setting the flag True to initiate the optimisation
    if len(geohashes) == 0:  # if empty list of geohash is supplied return False
        return False
    len_desired_reached = False  # Indicator for lenght of desired geohash level reached or not, set to False to start optimisation
    no_of_cycle = 0  # number of cycles to reach desired geohash level
    if smallest_gh_size < gh_input_level:
        cutoff = (gh_input_level - smallest_gh_size) + (
            smallest_gh_size - largest_gh_size
        )
    else:
        cutoff = smallest_gh_size - largest_gh_size
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
            # cut short geohash only if the string length is greater than largest geohash size (smaller in string length)
            if geohash_length >= largest_gh_size:
                # substring value to generate all combination of child geohashes
                geohash_1up = geohash[:-1]
                # If a geohash has been processed, skip it.
                if (geohash_1up not in geohash_processed_check) and (
                    geohash not in geohash_processed_check
                ):
                    # Generating combinations
                    combinations = set([geohash_1up + i for i in base32])
                    # intersections of ideal vs real geohash childs in a parent geohash
                    intersect = combinations.intersection(geohashes)
                    # condition to process the geohash and add to processed list
                    if combinations.issubset(geohashes) or (
                        len(intersect) >= 32 * (1 - percentage_error / 100)
                        and no_of_cycle < 1
                    ):
                        # add to processed geohash list
                        processed_geohash_set.add(geohash_1up)
                        # check list for processes geohash
                        geohash_processed_check.add(geohash_1up)
                    else:
                        # if not add it to processes list anyway
                        geohash_processed_check.add(geohash)
                        # if forced optimisation is required
                        if (
                            geohash_length >= smallest_gh_size
                            and forced_gh_upscale == True
                        ):
                            processed_geohash_set.add(geohash[:smallest_gh_size])
                        else:
                            processed_geohash_set.add(geohash)
        no_of_cycle = no_of_cycle + 1
        if len_desired_reached == True or no_of_cycle >= (cutoff):
            flag = False
        geohashes.clear()
        geohashes = geohashes.union(processed_geohash_set)  # adding the processed list
    geohashes = list(set(geohashes))
    return geohashes  # retuning final geohash list
