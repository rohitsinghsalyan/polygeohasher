#!/usr/bin/python
"""
Class-based API for polygeohasher package.

This module provides the Polygeohasher class that wraps the functional API
in an object-oriented interface for users who prefer class-based workflows.
"""

from typing import Optional
import pandas as pd
import geopandas as gpd

from polygeohasher import core


class Polygeohasher:
    """
    Class-based interface for polygon to geohash conversion and optimization.
    
    This class provides an object-oriented wrapper around the functional API,
    maintaining a GeoDataFrame instance and providing methods that operate on it.
    
    Attributes:
        gdf (gpd.GeoDataFrame): The GeoDataFrame containing geometries to process.
        
    Example:
        >>> import geopandas as gpd
        >>> from shapely.geometry import Polygon
        >>> gdf = gpd.GeoDataFrame({'geometry': [Polygon([(0,0), (1,0), (1,1), (0,1)])]})
        >>> pgh = Polygeohasher(gdf)
        >>> result = pgh.create_geohash_list(5)
        >>> 'geohash_list' in result.columns
        True
    """

    def __init__(self, gdf: gpd.GeoDataFrame) -> None:
        """
        Initialize Polygeohasher with a GeoDataFrame.
        
        Args:
            gdf: GeoDataFrame containing geometry column to process.
            
        Raises:
            TypeError: If gdf is not a GeoDataFrame.
            ValueError: If gdf does not contain a geometry column and is not empty.
        """
        if not isinstance(gdf, gpd.GeoDataFrame):
            raise TypeError("Input must be a GeoDataFrame")
        # Allow empty GeoDataFrames for cases where only static methods are used
        if len(gdf) > 0 and 'geometry' not in gdf.columns:
            raise ValueError("GeoDataFrame must contain a 'geometry' column")
        self.gdf = gdf
        
    def create_geohash_list(self, geohash_level: int, inner: bool = False) -> pd.DataFrame:
        """
        Convert geometries in the instance GeoDataFrame to geohash lists.
        
        This method wraps the functional API create_geohash_list function,
        operating on the GeoDataFrame stored in this instance.
        
        Args:
            geohash_level: Level of precision for geohash (1-12). Higher values 
                          provide more detailed coverage.
            inner: If True, only include geohashes completely inside the polygon.
                   If False, include geohashes that intersect with the polygon.
                   Defaults to False.
        
        Returns:
            DataFrame with geohash_list column containing lists of geohashes 
            for each geometry. The original geometry column is removed.
            
        Raises:
            ValueError: If geohash_level is not between 1 and 12.
            
        Example:
            >>> import geopandas as gpd
            >>> from shapely.geometry import Polygon
            >>> gdf = gpd.GeoDataFrame({'geometry': [Polygon([(0,0), (1,0), (1,1), (0,1)])]})
            >>> pgh = Polygeohasher(gdf)
            >>> result = pgh.create_geohash_list(5)
            >>> isinstance(result, pd.DataFrame)
            True
        """
        return core.create_geohash_list(self.gdf, geohash_level, inner)
    
    def geohash_optimizer(
        self, 
        gdf_with_geohashes: pd.DataFrame, 
        largest_gh_size: int, 
        smallest_gh_size: int, 
        gh_input_level: int, 
        percentage_error: float = 10, 
        forced_gh_upscale: bool = False
    ) -> pd.DataFrame:
        """
        Optimize geohash lists by combining adjacent geohashes into larger ones.
        
        This method wraps the functional API geohash_optimizer function to provide
        an object-oriented interface for geohash optimization.
        
        Args:
            gdf_with_geohashes: DataFrame with geohash_list column to optimize.
            largest_gh_size: Maximum geohash precision level (minimum string length).
                           Larger values mean shorter, less precise geohashes.
            smallest_gh_size: Minimum geohash precision level (maximum string length).
                            Smaller values mean longer, more precise geohashes.
            gh_input_level: Input geohash precision level from create_geohash_list.
            percentage_error: Allowed error percentage for optimization (0-100).
                            Higher values allow more aggressive optimization.
                            Defaults to 10.
            forced_gh_upscale: Force upscaling to smallest_gh_size even when
                             optimization criteria aren't met. Defaults to False.
        
        Returns:
            DataFrame with optimized_geohash_list column containing optimized 
            geohashes. Each row represents a unique optimized geohash.
            
        Raises:
            ValueError: If percentage_error is not between 0 and 100.
            KeyError: If gdf_with_geohashes doesn't contain 'geohash_list' column.
            
        Example:
            >>> df = pd.DataFrame({'geohash_list': [['9q8yy', '9q8yz']]})
            >>> pgh = Polygeohasher(gpd.GeoDataFrame())  # Empty for this example
            >>> result = pgh.geohash_optimizer(df, 3, 5, 5)
            >>> 'optimized_geohash_list' in result.columns
            True
        """
        return core.geohash_optimizer(
            gdf_with_geohashes, 
            largest_gh_size, 
            smallest_gh_size, 
            gh_input_level, 
            percentage_error, 
            forced_gh_upscale
        )

    @staticmethod
    def geohashes_to_geometry(
        df: pd.DataFrame, 
        geohash_column_name: str = "optimized_geohash_list"
    ) -> gpd.GeoDataFrame:
        """
        Convert geohashes in a DataFrame to geometries for visualization.
        
        This static method wraps the functional API geohashes_to_geometry function,
        providing a class-based interface for converting geohashes back to geometries.
        
        Args:
            df: DataFrame containing geohash column to convert.
            geohash_column_name: Name of the column containing geohashes.
                               Defaults to "optimized_geohash_list".
        
        Returns:
            GeoDataFrame with geometry column suitable for visualization,
            mapping, and export to spatial formats.
            
        Raises:
            KeyError: If the specified geohash column doesn't exist in df.
            
        Example:
            >>> df = pd.DataFrame({'optimized_geohash_list': ['9q8yy', '9q8yz']})
            >>> result = Polygeohasher.geohashes_to_geometry(df)
            >>> isinstance(result, gpd.GeoDataFrame)
            True
        """
        return core.geohashes_to_geometry(df, geohash_column_name)

    @staticmethod
    def optimization_summary(initial_gdf: pd.DataFrame, final_gdf: pd.DataFrame) -> None:
        """
        Print summary statistics of geohash optimization results.
        
        This static method wraps the functional API optimization_summary function,
        providing a class-based interface for displaying optimization statistics.
        
        Args:
            initial_gdf: DataFrame with initial geohash_list column before optimization.
            final_gdf: DataFrame with optimized geohashes after optimization.
            
        Raises:
            KeyError: If initial_gdf doesn't contain 'geohash_list' column.
            
        Example:
            >>> initial = pd.DataFrame({'geohash_list': [['a', 'b', 'c', 'd']]})
            >>> final = pd.DataFrame({'optimized_geohash_list': ['ab']})
            >>> Polygeohasher.optimization_summary(initial, final)  # doctest: +SKIP
            --------------------------------------------------
            OPTIMIZATION SUMMARY
            --------------------------------------------------
            Total Counts of Initial Geohashes :  4
            Total Counts of Final Geohashes   :  1
            Percent of optimization           :  75.0 %
            --------------------------------------------------
        """
        return core.optimization_summary(initial_gdf, final_gdf)


