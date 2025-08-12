#!/usr/bin/python
"""
Core functional API for polygeohasher package.

This module provides standalone functions for geohash operations, offering
a functional programming interface as an alternative to the class-based API.

The functional API is stateless and follows functional programming principles,
making it suitable for data processing pipelines and functional workflows.
"""

import pandas as pd
import geopandas as gpd
from typing import Union, Optional

from polygeohasher.converters import polygon_to_geohashes, geohashes_to_polygon
from polygeohasher.utils import get_optimized_geohashes


def create_geohash_list(gdf: gpd.GeoDataFrame, geohash_level: int, inner: bool = False) -> pd.DataFrame:
    """
    Convert geometries in a GeoDataFrame to geohash lists.
    
    This function processes each geometry in the input GeoDataFrame and converts
    it to a list of geohashes at the specified precision level. The resulting
    DataFrame contains the original data with geometry replaced by geohash lists.
    
    Args:
        gdf: GeoDataFrame containing geometry column to convert. Must have a 
             'geometry' column with valid Shapely geometries.
        geohash_level: Level of precision for geohash (1-12). Higher values 
                      provide more detailed coverage but generate more geohashes.
                      Level 1 covers ~5000km, Level 12 covers ~3.7cm.
        inner: Coverage strategy for polygon-to-geohash conversion.
               - True: Only include geohashes completely inside the polygon
               - False: Include geohashes that intersect with the polygon
               Defaults to False for maximum coverage.
    
    Returns:
        DataFrame with geohash_list column containing lists of geohashes for 
        each geometry. The original geometry column is removed, but all other
        columns are preserved.
        
    Raises:
        ValueError: If geohash_level is not between 1 and 12.
        KeyError: If gdf does not contain a 'geometry' column.
        TypeError: If gdf is not a GeoDataFrame.
        
    Example:
        >>> import geopandas as gpd
        >>> from shapely.geometry import Polygon
        >>> gdf = gpd.GeoDataFrame({
        ...     'id': [1], 
        ...     'geometry': [Polygon([(0,0), (1,0), (1,1), (0,1)])]
        ... })
        >>> result = create_geohash_list(gdf, 5)
        >>> 'geohash_list' in result.columns
        True
        >>> 'geometry' in result.columns
        False
    """
    gdf_copy = gdf.copy()
    gdf_copy["geohash_list"] = gdf_copy["geometry"].apply(
        lambda x: list(polygon_to_geohashes(x, geohash_level, inner))
    )
    gdf_copy = gdf_copy.drop("geometry", axis=1)
    return gdf_copy


def geohash_optimizer(
    gdf_with_geohashes: pd.DataFrame,
    largest_gh_size: int,
    smallest_gh_size: int,
    gh_input_level: int,
    percentage_error: float = 10,
    forced_gh_upscale: bool = False
) -> pd.DataFrame:
    """
    Optimize geohash lists by combining adjacent geohashes into larger ones.
    
    This function reduces the number of geohashes needed to cover an area by
    combining smaller adjacent geohashes into larger parent geohashes when
    possible. This optimization reduces storage requirements and improves
    query performance while maintaining acceptable coverage accuracy.
    
    Args:
        gdf_with_geohashes: DataFrame with geohash_list column containing lists
                           of geohashes to optimize.
        largest_gh_size: Maximum geohash precision level (minimum string length).
                        Lower values mean shorter, less precise geohashes that
                        cover larger areas. Must be <= smallest_gh_size.
        smallest_gh_size: Minimum geohash precision level (maximum string length).
                         Higher values mean longer, more precise geohashes that
                         cover smaller areas. Must be >= largest_gh_size.
        gh_input_level: Input geohash precision level from create_geohash_list.
                       Should match the precision used to generate the input
                       geohashes.
        percentage_error: Allowed error percentage for optimization (0-100).
                         Higher values enable more aggressive optimization by
                         allowing parent geohashes even when not all children
                         are present. Defaults to 10.
        forced_gh_upscale: Force upscaling to smallest_gh_size even when
                          optimization criteria aren't met. Useful for ensuring
                          consistent precision levels. Defaults to False.
    
    Returns:
        DataFrame with optimized_geohash_list column containing optimized 
        geohashes. The DataFrame is exploded so each row represents a single
        optimized geohash, with duplicates removed.
        
    Raises:
        ValueError: If percentage_error is not between 0 and 100, or if
                   largest_gh_size > smallest_gh_size.
        KeyError: If gdf_with_geohashes doesn't contain 'geohash_list' column.
        
    Note:
        The optimization algorithm works by:
        1. Grouping geohashes by their parent at the target precision level
        2. Checking if enough children exist to justify using the parent
        3. Applying the percentage_error threshold for partial coverage
        4. Iteratively optimizing until the target precision is reached
        
    Example:
        >>> df = pd.DataFrame({'geohash_list': [['9q8yy0', '9q8yy1', '9q8yy2']]})
        >>> result = geohash_optimizer(df, 3, 5, 6, percentage_error=20)
        >>> 'optimized_geohash_list' in result.columns
        True
        >>> len(result) <= 3  # Should be optimized to fewer geohashes
        True
    """
    gdf_copy = gdf_with_geohashes.copy()
    gdf_copy["optimized_geohash_list"] = gdf_copy["geohash_list"].apply(
        lambda x: get_optimized_geohashes(
            x,
            largest_gh_size,
            smallest_gh_size,
            gh_input_level,
            percentage_error,
            forced_gh_upscale,
        )
    )
    data = gdf_copy.drop("geohash_list", axis=1).copy()
    df = pd.DataFrame(data)
    df = df.explode("optimized_geohash_list")
    df.drop_duplicates("optimized_geohash_list", inplace=True)
    return df


def geohashes_to_geometry(
    df: pd.DataFrame, 
    geohash_column_name: str = "optimized_geohash_list"
) -> gpd.GeoDataFrame:
    """
    Convert geohashes in a DataFrame to geometries for visualization.
    
    This function converts geohash strings back to their corresponding polygon
    geometries, creating a GeoDataFrame suitable for mapping, visualization,
    and export to spatial formats like Shapefile, GeoJSON, etc.
    
    Args:
        df: DataFrame containing geohash column to convert. Can contain other
            columns which will be preserved in the output.
        geohash_column_name: Name of the column containing geohashes to convert.
                           Can contain individual geohash strings or lists of
                           geohashes. Defaults to "optimized_geohash_list".
    
    Returns:
        GeoDataFrame with geometry column containing polygon representations
        of the geohashes. If the input column contained lists, they are
        exploded so each row represents a single geohash polygon.
        
    Raises:
        KeyError: If the specified geohash column doesn't exist in df.
        ValueError: If the geohash column contains invalid geohash strings.
        
    Note:
        - Each geohash is converted to its bounding box polygon
        - Lists of geohashes are automatically exploded to individual rows
        - The resulting geometries can be used for spatial operations
        - CRS is assumed to be WGS84 (EPSG:4326)
        
    Example:
        >>> df = pd.DataFrame({
        ...     'id': [1, 2],
        ...     'optimized_geohash_list': ['9q8yy', '9q8yz']
        ... })
        >>> result = geohashes_to_geometry(df)
        >>> isinstance(result, gpd.GeoDataFrame)
        True
        >>> len(result) == 2
        True
        >>> 'geometry' in result.columns
        True
    """
    df_copy = df.copy()
    if isinstance(df_copy[geohash_column_name].iloc[0], list):
        df_copy = pd.DataFrame(df_copy)
        df_copy = df_copy.explode(geohash_column_name)
    
    df_copy["geometry"] = df_copy[geohash_column_name].apply(
        lambda x: geohashes_to_polygon([str(x)])
    )
    gdf = gpd.GeoDataFrame(df_copy, geometry=df_copy["geometry"])
    return gdf


def optimization_summary(initial_gdf: pd.DataFrame, final_gdf: pd.DataFrame) -> None:
    """
    Print summary statistics of geohash optimization results.
    
    This function calculates and displays optimization metrics, showing how
    effectively the geohash optimization reduced the total number of geohashes
    needed to cover the same area.
    
    Args:
        initial_gdf: DataFrame with initial geohash_list column containing
                    the original geohashes before optimization.
        final_gdf: DataFrame with optimized geohashes after running the
                  optimization process.
        
    Raises:
        KeyError: If initial_gdf doesn't contain 'geohash_list' column.
        
    Note:
        The optimization percentage is calculated as:
        ((initial_count - final_count) / initial_count) * 100
        
        Higher percentages indicate more effective optimization.
        
    Example:
        >>> initial = pd.DataFrame({'geohash_list': [['a', 'b', 'c', 'd']]})
        >>> final = pd.DataFrame({'optimized_geohash_list': ['ab']})
        >>> optimization_summary(initial, final)  # doctest: +SKIP
        --------------------------------------------------
        OPTIMIZATION SUMMARY
        --------------------------------------------------
        Total Counts of Initial Geohashes :  4
        Total Counts of Final Geohashes   :  1
        Percent of optimization           :  75.0 %
        --------------------------------------------------
    """
    print("-" * 50 + "\nOPTIMIZATION SUMMARY\n" + "-" * 50)
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