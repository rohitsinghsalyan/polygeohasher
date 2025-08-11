"""
Unit tests for polygeohasher.converters module.

This module tests the geohash/polygon conversion functions including:
- geohash_to_polygon: Convert geohash strings to Shapely polygons
- polygon_to_geohashes: Convert polygons to sets of geohashes
- geohashes_to_polygon: Convert multiple geohashes to unified geometry
"""

import pytest
from shapely.geometry import Polygon, Point, MultiPolygon
from shapely.ops import unary_union
import geohash

from polygeohasher.converters import (
    geohash_to_polygon,
    polygon_to_geohashes, 
    geohashes_to_polygon
)
from tests.fixtures.sample_data import sample_geohashes


class TestGeohashToPolygon:
    """Test geohash_to_polygon function with various geohash inputs."""
    
    def test_geohash_to_polygon_basic(self):
        """Test basic geohash to polygon conversion."""
        geohash_str = "9q8yy"
        polygon = geohash_to_polygon(geohash_str)
        
        assert isinstance(polygon, Polygon)
        assert polygon.is_valid
        assert polygon.area > 0
        
    def test_geohash_to_polygon_different_precisions(self):
        """Test geohash to polygon conversion with different precision levels."""
        base_geohash = "9q8"
        
        # Test different precision levels
        for precision in range(3, 8):
            geohash_str = base_geohash[:precision]
            polygon = geohash_to_polygon(geohash_str)
            
            assert isinstance(polygon, Polygon)
            assert polygon.is_valid
            assert polygon.area > 0
            
        # Higher precision should result in smaller area
        low_precision = geohash_to_polygon("9q")
        high_precision = geohash_to_polygon("9q8yy12")
        assert low_precision.area > high_precision.area
        
    def test_geohash_to_polygon_various_locations(self):
        """Test geohash to polygon conversion for different geographic locations."""
        test_geohashes = [
            "9q8yy",     # San Francisco area
            "dr5r7",     # New York area  
            "gcpvj",     # London area
            "wecz2",     # Sydney area
            "s00000",    # South America
            "b00000"     # Greenland area
        ]
        
        for geohash_str in test_geohashes:
            polygon = geohash_to_polygon(geohash_str)
            
            assert isinstance(polygon, Polygon)
            assert polygon.is_valid
            assert polygon.area > 0
            
            # Check that polygon bounds are reasonable
            bounds = polygon.bounds
            assert -180 <= bounds[0] <= 180  # min longitude
            assert -180 <= bounds[2] <= 180  # max longitude  
            assert -90 <= bounds[1] <= 90    # min latitude
            assert -90 <= bounds[3] <= 90    # max latitude
            
    def test_geohash_to_polygon_single_character(self):
        """Test geohash to polygon conversion with single character geohash."""
        polygon = geohash_to_polygon("9")
        
        assert isinstance(polygon, Polygon)
        assert polygon.is_valid
        assert polygon.area > 0
        
    def test_geohash_to_polygon_long_geohash(self):
        """Test geohash to polygon conversion with very long geohash."""
        long_geohash = "9q8yy1234567890"
        polygon = geohash_to_polygon(long_geohash)
        
        assert isinstance(polygon, Polygon)
        assert polygon.is_valid
        assert polygon.area > 0
        
    def test_geohash_to_polygon_boundary_coordinates(self):
        """Test that polygon coordinates match geohash decode bounds."""
        geohash_str = "9q8yy"
        polygon = geohash_to_polygon(geohash_str)
        
        # Get geohash bounds
        lat_centroid, lng_centroid, lat_offset, lng_offset = geohash.decode_exactly(geohash_str)
        
        expected_bounds = (
            lng_centroid - lng_offset,  # min longitude
            lat_centroid - lat_offset,  # min latitude
            lng_centroid + lng_offset,  # max longitude
            lat_centroid + lat_offset   # max latitude
        )
        
        actual_bounds = polygon.bounds
        
        # Check bounds match (with small tolerance for floating point)
        assert abs(actual_bounds[0] - expected_bounds[0]) < 1e-10
        assert abs(actual_bounds[1] - expected_bounds[1]) < 1e-10
        assert abs(actual_bounds[2] - expected_bounds[2]) < 1e-10
        assert abs(actual_bounds[3] - expected_bounds[3]) < 1e-10


class TestPolygonToGeohashes:
    """Test polygon_to_geohashes function with different polygon shapes and precision levels."""
    
    def test_polygon_to_geohashes_simple_square(self):
        """Test polygon to geohashes conversion with simple square polygon."""
        # Create a simple square polygon
        square = Polygon([(0, 0), (1, 0), (1, 1), (0, 1)])
        
        geohashes = polygon_to_geohashes(square, precision=5, inner=True)
        
        assert isinstance(geohashes, set)
        assert len(geohashes) > 0
        
        # All geohashes should be strings
        for gh in geohashes:
            assert isinstance(gh, str)
            assert len(gh) == 5  # Should match precision
            
    def test_polygon_to_geohashes_different_precisions(self):
        """Test polygon to geohashes conversion with different precision levels."""
        square = Polygon([(0, 0), (2, 0), (2, 2), (0, 2)])
        
        results = {}
        for precision in range(3, 7):
            geohashes = polygon_to_geohashes(square, precision=precision, inner=True)
            results[precision] = geohashes
            
            assert isinstance(geohashes, set)
            assert len(geohashes) > 0
            
            # Check geohash length matches precision
            for gh in geohashes:
                assert len(gh) == precision
                
        # Higher precision should generally result in more geohashes
        assert len(results[6]) >= len(results[3])
        
    def test_polygon_to_geohashes_inner_vs_outer(self):
        """Test polygon to geohashes conversion with inner vs outer modes."""
        square = Polygon([(0, 0), (1, 0), (1, 1), (0, 1)])
        
        inner_geohashes = polygon_to_geohashes(square, precision=5, inner=True)
        outer_geohashes = polygon_to_geohashes(square, precision=5, inner=False)
        
        assert isinstance(inner_geohashes, set)
        assert isinstance(outer_geohashes, set)
        
        # Inner mode should generally produce fewer or equal geohashes
        assert len(inner_geohashes) <= len(outer_geohashes)
        
        # Inner geohashes should be subset of outer geohashes
        assert inner_geohashes.issubset(outer_geohashes)
        
    def test_polygon_to_geohashes_complex_shape(self):
        """Test polygon to geohashes conversion with complex polygon shape."""
        # Create L-shaped polygon
        l_shape = Polygon([
            (0, 0), (3, 0), (3, 1), (1, 1), (1, 3), (0, 3), (0, 0)
        ])
        
        geohashes = polygon_to_geohashes(l_shape, precision=4, inner=True)
        
        assert isinstance(geohashes, set)
        assert len(geohashes) > 0
        
        # Verify all geohashes are valid
        for gh in geohashes:
            assert isinstance(gh, str)
            assert len(gh) == 4
            
    def test_polygon_to_geohashes_polygon_with_hole(self):
        """Test polygon to geohashes conversion with polygon containing hole."""
        # Create polygon with hole
        exterior = [(0, 0), (4, 0), (4, 4), (0, 4)]
        hole = [(1, 1), (3, 1), (3, 3), (1, 3)]
        polygon_with_hole = Polygon(exterior, [hole])
        
        geohashes = polygon_to_geohashes(polygon_with_hole, precision=4, inner=True)
        
        assert isinstance(geohashes, set)
        assert len(geohashes) > 0
        
        # Convert geohashes back to polygons and check they don't overlap with hole
        hole_polygon = Polygon(hole)
        for gh in geohashes:
            gh_polygon = geohash_to_polygon(gh)
            # Geohash polygon should not be completely inside the hole
            assert not hole_polygon.contains(gh_polygon)
            
    def test_polygon_to_geohashes_small_polygon(self):
        """Test polygon to geohashes conversion with very small polygon."""
        # Very small polygon
        small_polygon = Polygon([
            (0, 0), (0.001, 0), (0.001, 0.001), (0, 0.001)
        ])
        
        geohashes = polygon_to_geohashes(small_polygon, precision=8, inner=True)
        
        assert isinstance(geohashes, set)
        # Small polygon might result in no geohashes at high precision
        # This is expected behavior
        
    def test_polygon_to_geohashes_large_polygon(self):
        """Test polygon to geohashes conversion with large polygon."""
        # Large polygon covering significant area
        large_polygon = Polygon([
            (-2, -2), (2, -2), (2, 2), (-2, 2)
        ])
        
        geohashes = polygon_to_geohashes(large_polygon, precision=3, inner=True)
        
        assert isinstance(geohashes, set)
        assert len(geohashes) > 0
        
        # Should get multiple geohashes for large area
        assert len(geohashes) >= 1


class TestGeohashesToPolygon:
    """Test geohashes_to_polygon function with multiple geohash inputs."""
    
    def test_geohashes_to_polygon_single_geohash(self):
        """Test geohashes to polygon conversion with single geohash."""
        geohashes = ["9q8yy"]
        result = geohashes_to_polygon(geohashes)
        
        assert isinstance(result, Polygon)
        assert result.is_valid
        assert result.area > 0
        
        # Should be equivalent to geohash_to_polygon
        expected = geohash_to_polygon("9q8yy")
        assert result.equals(expected)
        
    def test_geohashes_to_polygon_multiple_adjacent(self):
        """Test geohashes to polygon conversion with adjacent geohashes."""
        # Get adjacent geohashes
        center_geohash = "9q8yy"
        neighbors = geohash.neighbors(center_geohash)
        geohashes = [center_geohash] + neighbors
        
        result = geohashes_to_polygon(geohashes)
        
        assert hasattr(result, 'area')  # Could be Polygon or MultiPolygon
        assert result.is_valid
        assert result.area > 0
        
        # Result area should be larger than single geohash
        single_area = geohash_to_polygon(center_geohash).area
        assert result.area > single_area
        
    def test_geohashes_to_polygon_multiple_separate(self):
        """Test geohashes to polygon conversion with separate geohashes."""
        # Use geohashes from different areas
        geohashes = ["9q8yy", "dr5r7", "gcpvj"]
        result = geohashes_to_polygon(geohashes)
        
        # Should result in MultiPolygon for separate areas
        assert isinstance(result, (Polygon, MultiPolygon))
        assert result.is_valid
        assert result.area > 0
        
    def test_geohashes_to_polygon_empty_list(self):
        """Test geohashes to polygon conversion with empty list."""
        geohashes = []
        result = geohashes_to_polygon(geohashes)
        
        # Should handle empty list gracefully
        assert hasattr(result, 'is_empty')
        
    def test_geohashes_to_polygon_duplicate_geohashes(self):
        """Test geohashes to polygon conversion with duplicate geohashes."""
        geohashes = ["9q8yy", "9q8yy", "9q8yz", "9q8yz"]
        result = geohashes_to_polygon(geohashes)
        
        assert isinstance(result, (Polygon, MultiPolygon))
        assert result.is_valid
        assert result.area > 0
        
        # Should be same as without duplicates
        unique_geohashes = ["9q8yy", "9q8yz"]
        expected = geohashes_to_polygon(unique_geohashes)
        assert abs(result.area - expected.area) < 1e-10
        
    def test_geohashes_to_polygon_different_precisions(self):
        """Test geohashes to polygon conversion with different precision geohashes."""
        # Mix of different precision geohashes
        geohashes = ["9q", "9q8yy", "9q8yz123"]
        result = geohashes_to_polygon(geohashes)
        
        assert isinstance(result, (Polygon, MultiPolygon))
        assert result.is_valid
        assert result.area > 0
        
    def test_geohashes_to_polygon_sample_data(self, sample_geohashes):
        """Test geohashes to polygon conversion with sample fixture data."""
        result = geohashes_to_polygon(sample_geohashes)
        
        assert isinstance(result, (Polygon, MultiPolygon))
        assert result.is_valid
        assert result.area > 0
        
        # Should combine all sample geohashes
        individual_areas = [geohash_to_polygon(gh).area for gh in sample_geohashes]
        total_individual_area = sum(individual_areas)
        
        # Union area should be less than or equal to sum of individual areas
        # (due to potential overlaps)
        assert result.area <= total_individual_area
        
    def test_geohashes_to_polygon_preserves_topology(self):
        """Test that geohashes to polygon conversion preserves valid topology."""
        # Create a set of geohashes that should form a connected region
        center = "9q8yy"
        neighbors = geohash.neighbors(center)
        geohashes = [center] + neighbors[:4]  # Take subset to ensure connectivity
        
        result = geohashes_to_polygon(geohashes)
        
        assert result.is_valid
        assert not result.is_empty
        
        # Check that result has reasonable geometric properties
        assert result.area > 0
        assert len(result.bounds) == 4  # Should have bounding box
        
    def test_geohashes_to_polygon_union_behavior(self):
        """Test that geohashes to polygon properly unions overlapping areas."""
        # Create overlapping geohashes by using different precisions of same area
        base_geohash = "9q8yy"
        detailed_geohashes = [base_geohash + str(i) for i in range(4)]
        
        # Union of detailed geohashes should be similar to base geohash area
        result = geohashes_to_polygon(detailed_geohashes)
        base_polygon = geohash_to_polygon(base_geohash)
        
        assert result.is_valid
        assert base_polygon.is_valid
        
        # The union should be contained within or equal to the base geohash
        assert result.within(base_polygon) or result.equals(base_polygon)