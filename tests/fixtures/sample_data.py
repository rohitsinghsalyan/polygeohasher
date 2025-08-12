"""
Sample data and fixtures for polygeohasher tests.

This module contains all shared test data, fixtures, and constants used across
the test suite to ensure consistency and reduce duplication.
"""

import geopandas as gpd
import pandas as pd
from shapely.geometry import Polygon, Point
import pytest
import os

# Test data paths
SAMPLE_GEOJSON_PATH = "example/sample.geojson"

# Test constants
TEST_GEOHASH_LEVELS = [4, 5, 6, 7, 8]
TEST_OPTIMIZATION_PARAMS = {
    'largest_gh_size': 5,
    'smallest_gh_size': 7, 
    'gh_input_level': 6,
    'error_threshold': 0.1
}

# Sample geohashes for testing
SAMPLE_GEOHASHES = [
    'tdr1y',
    'tdr1z', 
    'tdr20',
    'tdr21',
    'tdr24',
    'tdr25'
]


@pytest.fixture
def sample_gdf():
    """
    Load the main sample GeoDataFrame from example/sample.geojson.
    
    Returns:
        gpd.GeoDataFrame: GeoDataFrame with 4 polygon features representing
                         different regions (South East, North West, North East, South West)
    """
    if os.path.exists(SAMPLE_GEOJSON_PATH):
        return gpd.read_file(SAMPLE_GEOJSON_PATH)
    else:
        # Fallback to creating simple test data if file doesn't exist
        return simple_polygon_gdf()


@pytest.fixture  
def simple_polygon_gdf():
    """
    Create a simple GeoDataFrame with basic polygon geometries for testing.
    
    Returns:
        gpd.GeoDataFrame: Simple GeoDataFrame with 2 polygon features
    """
    polygons = [
        Polygon([(0, 0), (1, 0), (1, 1), (0, 1)]),  # Unit square
        Polygon([(2, 2), (3, 2), (3, 3), (2, 3)])   # Another unit square
    ]
    
    gdf = gpd.GeoDataFrame({
        'Name': ['Square1', 'Square2'],
        'geometry': polygons
    })
    return gdf


@pytest.fixture
def complex_polygon_gdf():
    """
    Create a GeoDataFrame with more complex polygon geometries for edge case testing.
    
    Returns:
        gpd.GeoDataFrame: GeoDataFrame with complex polygon features
    """
    # Complex polygon with hole
    exterior = [(0, 0), (10, 0), (10, 10), (0, 10)]
    hole = [(2, 2), (8, 2), (8, 8), (2, 8)]
    complex_poly = Polygon(exterior, [hole])
    
    # Multi-part polygon
    poly1 = Polygon([(15, 0), (20, 0), (20, 5), (15, 5)])
    poly2 = Polygon([(15, 7), (20, 7), (20, 12), (15, 12)])
    
    gdf = gpd.GeoDataFrame({
        'Name': ['ComplexPoly', 'MultiPart1', 'MultiPart2'],
        'geometry': [complex_poly, poly1, poly2]
    })
    return gdf


@pytest.fixture
def empty_gdf():
    """
    Create an empty GeoDataFrame for testing edge cases.
    
    Returns:
        gpd.GeoDataFrame: Empty GeoDataFrame with proper schema
    """
    return gpd.GeoDataFrame({
        'Name': [],
        'geometry': []
    })


@pytest.fixture
def sample_geohashes():
    """
    Provide sample geohash strings for testing conversion functions.
    
    Returns:
        list: List of sample geohash strings
    """
    return SAMPLE_GEOHASHES.copy()


@pytest.fixture
def geohash_dataframe():
    """
    Create a DataFrame with geohash data for testing optimization functions.
    
    Returns:
        pd.DataFrame: DataFrame with geohash_list column
    """
    return pd.DataFrame({
        'Name': ['Region1', 'Region2', 'Region3'],
        'geohash_list': [
            ['tdr1y', 'tdr1z', 'tdr20'],
            ['tdr21', 'tdr24'], 
            ['tdr25', 'tdr26', 'tdr27', 'tdr28']
        ]
    })


@pytest.fixture
def optimization_test_data():
    """
    Provide test data specifically for optimization algorithm testing.
    
    Returns:
        dict: Dictionary containing test parameters and expected results
    """
    return {
        'input_geohashes': [
            ['tdr1y0', 'tdr1y1', 'tdr1y2', 'tdr1y3'],  # Can be optimized to 'tdr1y'
            ['tdr1z0', 'tdr1z1', 'tdr1z4', 'tdr1z5'],  # Partial optimization
            ['tdr20']  # Already optimal
        ],
        'expected_optimized': [
            ['tdr1y'],
            ['tdr1z0', 'tdr1z1', 'tdr1z4', 'tdr1z5'],  # No optimization possible
            ['tdr20']
        ],
        'optimization_params': TEST_OPTIMIZATION_PARAMS.copy()
    }


# Utility functions for test data creation
def create_test_gdf_with_geohashes(geohash_level=6):
    """
    Create a test GeoDataFrame that already has geohash_list column.
    
    Args:
        geohash_level (int): Precision level for geohashes
        
    Returns:
        pd.DataFrame: DataFrame with Name and geohash_list columns
    """
    # This would typically be created by running create_geohash_list
    # but we provide static data for testing
    return pd.DataFrame({
        'Name': ['TestRegion1', 'TestRegion2'],
        'geohash_list': [
            ['tdr1y', 'tdr1z', 'tdr20', 'tdr21'],
            ['tdr24', 'tdr25', 'tdr26']
        ]
    })


def create_expected_optimization_results():
    """
    Create expected results for optimization testing.
    
    Returns:
        dict: Dictionary with expected optimization outcomes
    """
    return {
        'initial_count': 2597,  # Based on current test expectations
        'optimized_count': 837,  # Based on current test expectations
        'compression_ratio': 0.32  # Approximate expected compression
    }