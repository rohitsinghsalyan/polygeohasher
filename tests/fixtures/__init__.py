"""
Test fixtures for polygeohasher package.

This module provides centralized test data and fixtures for use across all test modules.
"""

from .sample_data import *

__all__ = [
    'sample_gdf',
    'simple_polygon_gdf', 
    'complex_polygon_gdf',
    'empty_gdf',
    'sample_geohashes',
    'optimization_test_data',
    'SAMPLE_GEOJSON_PATH',
    'TEST_GEOHASH_LEVELS',
    'TEST_OPTIMIZATION_PARAMS'
]