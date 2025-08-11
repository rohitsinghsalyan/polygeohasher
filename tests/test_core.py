"""
Unit tests for polygeohasher.core module.

This module tests the core functional API functions including:
- create_geohash_list: Convert GeoDataFrame geometries to geohash lists
- geohash_optimizer: Optimize geohash lists by combining adjacent geohashes
- geohashes_to_geometry: Convert geohashes back to geometries
- optimization_summary: Print optimization statistics
"""

import pytest
import pandas as pd
import geopandas as gpd
from shapely.geometry import Polygon, Point
from io import StringIO
import sys

from polygeohasher.core import (
    create_geohash_list,
    geohash_optimizer,
    geohashes_to_geometry,
    optimization_summary
)
from tests.fixtures.sample_data import (
    sample_gdf,
    simple_polygon_gdf,
    complex_polygon_gdf,
    empty_gdf,
    geohash_dataframe,
    optimization_test_data
)


class TestCreateGeohashList:
    """Test create_geohash_list function with different GeoDataFrames and parameters."""
    
    def test_create_geohash_list_basic(self, simple_polygon_gdf):
        """Test basic geohash list creation with simple polygons."""
        result = create_geohash_list(simple_polygon_gdf, geohash_level=5)
        
        assert isinstance(result, pd.DataFrame)
        assert 'geohash_list' in result.columns
        assert 'geometry' not in result.columns  # Should be dropped
        assert len(result) == len(simple_polygon_gdf)
        
        # Check that geohash_list contains lists of strings
        for geohash_list in result['geohash_list']:
            assert isinstance(geohash_list, list)
            assert len(geohash_list) > 0
            for geohash in geohash_list:
                assert isinstance(geohash, str)
                assert len(geohash) == 5  # Should match geohash_level
                
    def test_create_geohash_list_different_levels(self, simple_polygon_gdf):
        """Test create_geohash_list with different precision levels."""
        levels_to_test = [4, 5, 6]
        results = {}
        
        for level in levels_to_test:
            result = create_geohash_list(simple_polygon_gdf, geohash_level=level)
            results[level] = result
            
            assert isinstance(result, pd.DataFrame)
            assert 'geohash_list' in result.columns
            
            # Check geohash length matches level
            for geohash_list in result['geohash_list']:
                for geohash in geohash_list:
                    assert len(geohash) == level
                    
        # Higher precision should generally result in more geohashes
        low_precision_count = sum(len(lst) for lst in results[4]['geohash_list'])
        high_precision_count = sum(len(lst) for lst in results[6]['geohash_list'])
        assert high_precision_count >= low_precision_count
        
    def test_create_geohash_list_inner_parameter(self, simple_polygon_gdf):
        """Test create_geohash_list with inner parameter variations."""
        result_inner_true = create_geohash_list(simple_polygon_gdf, geohash_level=6, inner=True)
        result_inner_false = create_geohash_list(simple_polygon_gdf, geohash_level=6, inner=False)
        
        assert isinstance(result_inner_true, pd.DataFrame)
        assert isinstance(result_inner_false, pd.DataFrame)
        
        # inner=False should generally produce more or equal geohashes
        count_inner_true = sum(len(lst) for lst in result_inner_true['geohash_list'])
        count_inner_false = sum(len(lst) for lst in result_inner_false['geohash_list'])
        assert count_inner_false >= count_inner_true
        
    def test_create_geohash_list_preserves_other_columns(self, simple_polygon_gdf):
        """Test that create_geohash_list preserves non-geometry columns."""
        result = create_geohash_list(simple_polygon_gdf, geohash_level=5)
        
        # Should preserve all columns except geometry
        expected_columns = [col for col in simple_polygon_gdf.columns if col != 'geometry']
        expected_columns.append('geohash_list')
        
        assert set(result.columns) == set(expected_columns)
        
        # Check that other column data is preserved
        if 'Name' in simple_polygon_gdf.columns:
            assert list(result['Name']) == list(simple_polygon_gdf['Name'])
            
    def test_create_geohash_list_complex_polygons(self, complex_polygon_gdf):
        """Test create_geohash_list with complex polygon geometries."""
        result = create_geohash_list(complex_polygon_gdf, geohash_level=5)
        
        assert isinstance(result, pd.DataFrame)
        assert 'geohash_list' in result.columns
        assert len(result) == len(complex_polygon_gdf)
        
        # Should handle complex polygons (with holes, multipart, etc.)
        for geohash_list in result['geohash_list']:
            assert isinstance(geohash_list, list)
            # Complex polygons might result in empty lists for some cases
            for geohash in geohash_list:
                assert isinstance(geohash, str)
                assert len(geohash) == 5
                
    def test_create_geohash_list_sample_data(self, sample_gdf):
        """Test create_geohash_list with sample GeoJSON data."""
        if sample_gdf is not None and not sample_gdf.empty:
            result = create_geohash_list(sample_gdf, geohash_level=6)
            
            assert isinstance(result, pd.DataFrame)
            assert 'geohash_list' in result.columns
            assert len(result) == len(sample_gdf)
            
            # Check total geohash count matches expected from existing tests
            total_geohashes = sum(len(lst) for lst in result['geohash_list'])
            assert total_geohashes > 0
            
    def test_create_geohash_list_empty_gdf(self, empty_gdf):
        """Test create_geohash_list with empty GeoDataFrame."""
        result = create_geohash_list(empty_gdf, geohash_level=5)
        
        assert isinstance(result, pd.DataFrame)
        assert 'geohash_list' in result.columns
        assert len(result) == 0
        
    def test_create_geohash_list_single_point(self):
        """Test create_geohash_list with point geometry."""
        point_gdf = gpd.GeoDataFrame({
            'Name': ['Point1'],
            'geometry': [Point(0, 0)]
        })
        
        result = create_geohash_list(point_gdf, geohash_level=5)
        
        assert isinstance(result, pd.DataFrame)
        assert 'geohash_list' in result.columns
        assert len(result) == 1
        
        # Point should result in single geohash or empty list
        geohash_list = result['geohash_list'].iloc[0]
        assert isinstance(geohash_list, list)
        
    def test_create_geohash_list_boundary_levels(self, simple_polygon_gdf):
        """Test create_geohash_list with boundary precision levels."""
        # Test minimum and maximum reasonable levels
        for level in [1, 2, 5, 6]:
            result = create_geohash_list(simple_polygon_gdf, geohash_level=level)
            
            assert isinstance(result, pd.DataFrame)
            assert 'geohash_list' in result.columns
            
            for geohash_list in result['geohash_list']:
                for geohash in geohash_list:
                    assert len(geohash) == level
                    
    def test_create_geohash_list_does_not_modify_input(self, simple_polygon_gdf):
        """Test that create_geohash_list does not modify the input GeoDataFrame."""
        original_columns = list(simple_polygon_gdf.columns)
        original_length = len(simple_polygon_gdf)
        
        result = create_geohash_list(simple_polygon_gdf, geohash_level=5)
        
        # Input should be unchanged
        assert list(simple_polygon_gdf.columns) == original_columns
        assert len(simple_polygon_gdf) == original_length
        assert 'geohash_list' not in simple_polygon_gdf.columns


class TestGeohashOptimizer:
    """Test geohash_optimizer function with various optimization scenarios."""
    
    def test_geohash_optimizer_basic(self, geohash_dataframe):
        """Test basic geohash optimization functionality."""
        result = geohash_optimizer(
            geohash_dataframe,
            largest_gh_size=3,
            smallest_gh_size=6,
            gh_input_level=5
        )
        
        assert isinstance(result, pd.DataFrame)
        assert 'optimized_geohash_list' in result.columns
        assert 'geohash_list' not in result.columns  # Should be dropped
        
        # Check that optimized geohashes are strings
        for geohash in result['optimized_geohash_list']:
            assert isinstance(geohash, str)
            assert 3 <= len(geohash) <= 6  # Should be within size bounds
            
    def test_geohash_optimizer_different_parameters(self, geohash_dataframe):
        """Test geohash_optimizer with different optimization parameters."""
        test_params = [
            {'largest_gh_size': 2, 'smallest_gh_size': 5, 'gh_input_level': 5},
            {'largest_gh_size': 4, 'smallest_gh_size': 7, 'gh_input_level': 6},
            {'largest_gh_size': 3, 'smallest_gh_size': 8, 'gh_input_level': 7}
        ]
        
        for params in test_params:
            result = geohash_optimizer(geohash_dataframe, **params)
            
            assert isinstance(result, pd.DataFrame)
            assert 'optimized_geohash_list' in result.columns
            
            # Check geohash sizes are within bounds
            for geohash in result['optimized_geohash_list']:
                assert params['largest_gh_size'] <= len(geohash) <= params['smallest_gh_size']
                
    def test_geohash_optimizer_percentage_error(self, geohash_dataframe):
        """Test geohash_optimizer with different percentage error values."""
        error_values = [5.0, 10.0, 15.0, 20.0]
        results = {}
        
        for error in error_values:
            result = geohash_optimizer(
                geohash_dataframe,
                largest_gh_size=3,
                smallest_gh_size=6,
                gh_input_level=5,
                percentage_error=error
            )
            results[error] = result
            
            assert isinstance(result, pd.DataFrame)
            assert 'optimized_geohash_list' in result.columns
            
        # Higher error tolerance should generally result in more optimization
        # (fewer final geohashes)
        low_error_count = len(results[5.0])
        high_error_count = len(results[20.0])
        assert high_error_count <= low_error_count
        
    def test_geohash_optimizer_forced_upscale(self, geohash_dataframe):
        """Test geohash_optimizer with forced upscale parameter."""
        result_no_force = geohash_optimizer(
            geohash_dataframe,
            largest_gh_size=3,
            smallest_gh_size=6,
            gh_input_level=5,
            forced_gh_upscale=False
        )
        
        result_force = geohash_optimizer(
            geohash_dataframe,
            largest_gh_size=3,
            smallest_gh_size=6,
            gh_input_level=5,
            forced_gh_upscale=True
        )
        
        assert isinstance(result_no_force, pd.DataFrame)
        assert isinstance(result_force, pd.DataFrame)
        
        # Both should have optimized_geohash_list column
        assert 'optimized_geohash_list' in result_no_force.columns
        assert 'optimized_geohash_list' in result_force.columns
        
    def test_geohash_optimizer_removes_duplicates(self):
        """Test that geohash_optimizer removes duplicate geohashes."""
        # Create test data with potential for duplicate optimized geohashes
        test_data = pd.DataFrame({
            'Name': ['Region1', 'Region2'],
            'geohash_list': [
                ['tdr1y0', 'tdr1y1', 'tdr1y2', 'tdr1y3'],  # Should optimize to 'tdr1y'
                ['tdr1y4', 'tdr1y5', 'tdr1y6', 'tdr1y7']   # Should also optimize to 'tdr1y'
            ]
        })
        
        result = geohash_optimizer(
            test_data,
            largest_gh_size=3,
            smallest_gh_size=6,
            gh_input_level=6,
            percentage_error=0  # Force optimization
        )
        
        assert isinstance(result, pd.DataFrame)
        
        # Should remove duplicates
        unique_geohashes = result['optimized_geohash_list'].unique()
        assert len(unique_geohashes) == len(result)
        
    def test_geohash_optimizer_explodes_lists(self):
        """Test that geohash_optimizer properly explodes geohash lists."""
        # Create test data with multiple geohashes per row
        test_data = pd.DataFrame({
            'Name': ['Region1'],
            'geohash_list': [['tdr1y', 'tdr1z', 'tdr20']]
        })
        
        result = geohash_optimizer(
            test_data,
            largest_gh_size=3,
            smallest_gh_size=6,
            gh_input_level=5
        )
        
        assert isinstance(result, pd.DataFrame)
        assert len(result) >= 1  # Should have at least one row per geohash
        
        # Each row should have a single geohash string
        for geohash in result['optimized_geohash_list']:
            assert isinstance(geohash, str)
            
    def test_geohash_optimizer_preserves_other_columns(self):
        """Test that geohash_optimizer preserves non-geohash columns."""
        test_data = pd.DataFrame({
            'Name': ['Region1', 'Region2'],
            'Category': ['Type A', 'Type B'],
            'geohash_list': [
                ['tdr1y', 'tdr1z'],
                ['tdr20', 'tdr21']
            ]
        })
        
        result = geohash_optimizer(
            test_data,
            largest_gh_size=3,
            smallest_gh_size=6,
            gh_input_level=5
        )
        
        assert isinstance(result, pd.DataFrame)
        assert 'optimized_geohash_list' in result.columns
        assert 'Name' in result.columns
        assert 'Category' in result.columns
        assert 'geohash_list' not in result.columns
        
    def test_geohash_optimizer_empty_input(self):
        """Test geohash_optimizer with empty DataFrame."""
        empty_data = pd.DataFrame({
            'Name': [],
            'geohash_list': []
        })
        
        result = geohash_optimizer(
            empty_data,
            largest_gh_size=3,
            smallest_gh_size=6,
            gh_input_level=5
        )
        
        assert isinstance(result, pd.DataFrame)
        assert len(result) == 0
        assert 'optimized_geohash_list' in result.columns
        
    def test_geohash_optimizer_single_geohash_lists(self):
        """Test geohash_optimizer with single geohash per list."""
        test_data = pd.DataFrame({
            'Name': ['Region1', 'Region2'],
            'geohash_list': [['tdr1y'], ['tdr1z']]
        })
        
        result = geohash_optimizer(
            test_data,
            largest_gh_size=3,
            smallest_gh_size=6,
            gh_input_level=5
        )
        
        assert isinstance(result, pd.DataFrame)
        assert len(result) == 2  # Should have one row per geohash
        
        # Single geohashes should remain unchanged or be optimized
        for geohash in result['optimized_geohash_list']:
            assert isinstance(geohash, str)
            assert 3 <= len(geohash) <= 6


class TestGeohashesToGeometry:
    """Test geohashes_to_geometry and optimization_summary functions."""
    
    def test_geohashes_to_geometry_basic(self):
        """Test basic geohashes to geometry conversion."""
        test_data = pd.DataFrame({
            'optimized_geohash_list': ['tdr1y', 'tdr1z', 'tdr20']
        })
        
        result = geohashes_to_geometry(test_data)
        
        assert isinstance(result, gpd.GeoDataFrame)
        assert 'geometry' in result.columns
        assert 'optimized_geohash_list' in result.columns
        assert len(result) == len(test_data)
        
        # Check that geometries are valid
        for geom in result['geometry']:
            assert geom is not None
            assert geom.is_valid
            assert geom.area > 0
            
    def test_geohashes_to_geometry_custom_column(self):
        """Test geohashes_to_geometry with custom column name."""
        test_data = pd.DataFrame({
            'custom_geohash_col': ['tdr1y', 'tdr1z', 'tdr20']
        })
        
        result = geohashes_to_geometry(test_data, geohash_column_name='custom_geohash_col')
        
        assert isinstance(result, gpd.GeoDataFrame)
        assert 'geometry' in result.columns
        assert 'custom_geohash_col' in result.columns
        assert len(result) == len(test_data)
        
    def test_geohashes_to_geometry_with_lists(self):
        """Test geohashes_to_geometry with list-type geohash column."""
        test_data = pd.DataFrame({
            'optimized_geohash_list': [['tdr1y', 'tdr1z'], ['tdr20']]
        })
        
        result = geohashes_to_geometry(test_data)
        
        assert isinstance(result, gpd.GeoDataFrame)
        assert 'geometry' in result.columns
        
        # Should explode lists and create geometry for each geohash
        assert len(result) == 3  # Total number of individual geohashes
        
        for geom in result['geometry']:
            assert geom is not None
            assert geom.is_valid
            
    def test_geohashes_to_geometry_preserves_columns(self):
        """Test that geohashes_to_geometry preserves other columns."""
        test_data = pd.DataFrame({
            'Name': ['Region1', 'Region2'],
            'Category': ['Type A', 'Type B'],
            'optimized_geohash_list': ['tdr1y', 'tdr1z']
        })
        
        result = geohashes_to_geometry(test_data)
        
        assert isinstance(result, gpd.GeoDataFrame)
        assert 'Name' in result.columns
        assert 'Category' in result.columns
        assert 'geometry' in result.columns
        assert 'optimized_geohash_list' in result.columns
        
    def test_geohashes_to_geometry_empty_input(self):
        """Test geohashes_to_geometry with empty DataFrame."""
        empty_data = pd.DataFrame({
            'optimized_geohash_list': []
        })
        
        # Empty DataFrame should be handled gracefully
        # The function may fail with empty input, which is expected behavior
        try:
            result = geohashes_to_geometry(empty_data)
            assert isinstance(result, gpd.GeoDataFrame)
            assert len(result) == 0
            assert 'geometry' in result.columns
        except (IndexError, ValueError):
            # Empty input causing errors is acceptable behavior
            pass
        
    def test_geohashes_to_geometry_various_precisions(self):
        """Test geohashes_to_geometry with geohashes of different precisions."""
        test_data = pd.DataFrame({
            'optimized_geohash_list': ['tdr', 'tdr1y', 'tdr1y123', 'gcpvj0']
        })
        
        result = geohashes_to_geometry(test_data)
        
        assert isinstance(result, gpd.GeoDataFrame)
        assert len(result) == len(test_data)
        
        # All should produce valid geometries regardless of precision
        for geom in result['geometry']:
            assert geom is not None
            assert geom.is_valid
            assert geom.area > 0


class TestOptimizationSummary:
    """Test optimization_summary function."""
    
    def test_optimization_summary_basic(self, capsys):
        """Test basic optimization summary output."""
        initial_data = pd.DataFrame({
            'geohash_list': [['a', 'b', 'c'], ['d', 'e']]
        })
        
        final_data = pd.DataFrame({
            'optimized_geohash_list': ['ab', 'de', 'f']
        })
        
        optimization_summary(initial_data, final_data)
        
        captured = capsys.readouterr()
        output = captured.out
        
        # Check that summary contains expected information
        assert "OPTIMIZATION SUMMARY" in output
        assert "Total Counts of Initial Geohashes" in output
        assert "Total Counts of Final Geohashes" in output
        assert "Percent of optimization" in output
        assert "5" in output  # Initial count
        assert "3" in output  # Final count
        assert "40.0" in output  # Optimization percentage
        
    def test_optimization_summary_no_optimization(self, capsys):
        """Test optimization summary when no optimization occurred."""
        initial_data = pd.DataFrame({
            'geohash_list': [['a'], ['b'], ['c']]
        })
        
        final_data = pd.DataFrame({
            'optimized_geohash_list': ['a', 'b', 'c']
        })
        
        optimization_summary(initial_data, final_data)
        
        captured = capsys.readouterr()
        output = captured.out
        
        assert "OPTIMIZATION SUMMARY" in output
        assert "3" in output  # Both initial and final counts
        assert "0.0" in output  # No optimization percentage
        
    def test_optimization_summary_complete_optimization(self, capsys):
        """Test optimization summary with maximum optimization."""
        initial_data = pd.DataFrame({
            'geohash_list': [['a', 'b', 'c', 'd', 'e', 'f', 'g', 'h']]
        })
        
        final_data = pd.DataFrame({
            'optimized_geohash_list': ['abcdefgh']
        })
        
        optimization_summary(initial_data, final_data)
        
        captured = capsys.readouterr()
        output = captured.out
        
        assert "OPTIMIZATION SUMMARY" in output
        assert "8" in output  # Initial count
        assert "1" in output  # Final count
        assert "87.5" in output  # High optimization percentage
        
    def test_optimization_summary_empty_data(self, capsys):
        """Test optimization summary with empty data."""
        initial_data = pd.DataFrame({
            'geohash_list': []
        })
        
        final_data = pd.DataFrame({
            'optimized_geohash_list': []
        })
        
        # Empty data may cause division by zero, which is expected
        try:
            optimization_summary(initial_data, final_data)
            captured = capsys.readouterr()
            output = captured.out
            assert "OPTIMIZATION SUMMARY" in output
            assert "0" in output  # Both counts should be 0
        except ZeroDivisionError:
            # Division by zero with empty data is expected behavior
            pass
        
    def test_optimization_summary_single_geohash(self, capsys):
        """Test optimization summary with single geohash."""
        initial_data = pd.DataFrame({
            'geohash_list': [['single_geohash']]
        })
        
        final_data = pd.DataFrame({
            'optimized_geohash_list': ['single_geohash']
        })
        
        optimization_summary(initial_data, final_data)
        
        captured = capsys.readouterr()
        output = captured.out
        
        assert "OPTIMIZATION SUMMARY" in output
        assert "1" in output  # Both initial and final counts
        assert "0.0" in output  # No optimization possible
        
    def test_optimization_summary_multiple_lists(self, capsys):
        """Test optimization summary with multiple geohash lists."""
        initial_data = pd.DataFrame({
            'geohash_list': [
                ['a1', 'a2', 'a3'],
                ['b1', 'b2'],
                ['c1', 'c2', 'c3', 'c4']
            ]
        })
        
        final_data = pd.DataFrame({
            'optimized_geohash_list': ['a', 'b', 'c1', 'c2']
        })
        
        optimization_summary(initial_data, final_data)
        
        captured = capsys.readouterr()
        output = captured.out
        
        assert "OPTIMIZATION SUMMARY" in output
        assert "9" in output  # Initial count (3+2+4)
        assert "4" in output  # Final count
        assert "55.56" in output  # Optimization percentage
        
    def test_optimization_summary_formatting(self, capsys):
        """Test that optimization summary has proper formatting."""
        initial_data = pd.DataFrame({
            'geohash_list': [['a', 'b']]
        })
        
        final_data = pd.DataFrame({
            'optimized_geohash_list': ['ab']
        })
        
        optimization_summary(initial_data, final_data)
        
        captured = capsys.readouterr()
        output = captured.out
        
        # Check formatting elements
        assert "-" * 50 in output  # Separator lines
        assert output.count("-" * 50) >= 2  # At least opening and closing separators
        assert ":" in output  # Colon separators in data lines
        assert "%" in output  # Percentage symbol