"""
Unit tests for polygeohasher.utils module.

This module tests the utility functions and constants including:
- get_optimized_geohashes: Core optimization algorithm for geohash lists
- BASE32: Base32 character set constant used for geohash encoding
"""

import pytest
from polygeohasher.utils import get_optimized_geohashes, BASE32


class TestBase32Constant:
    """Test BASE32 constant used for geohash encoding."""
    
    def test_base32_is_list(self):
        """Test that BASE32 is a list."""
        assert isinstance(BASE32, list)
        
    def test_base32_length(self):
        """Test that BASE32 has exactly 32 characters."""
        assert len(BASE32) == 32
        
    def test_base32_characters(self):
        """Test that BASE32 contains expected geohash characters."""
        expected_chars = "0123456789bcdefghjkmnpqrstuvwxyz"
        assert ''.join(BASE32) == expected_chars
        
    def test_base32_no_duplicates(self):
        """Test that BASE32 contains no duplicate characters."""
        assert len(BASE32) == len(set(BASE32))
        
    def test_base32_all_strings(self):
        """Test that all BASE32 elements are single character strings."""
        for char in BASE32:
            assert isinstance(char, str)
            assert len(char) == 1


class TestGetOptimizedGeohashes:
    """Test get_optimized_geohashes function with various optimization parameters."""
    
    def test_empty_geohash_list(self):
        """Test optimization with empty geohash list."""
        result = get_optimized_geohashes(
            geohashes=[],
            largest_gh_size=4,
            smallest_gh_size=6,
            gh_input_level=5
        )
        assert result is False
        
    def test_single_geohash(self):
        """Test optimization with single geohash."""
        geohashes = ['tdr1y']
        result = get_optimized_geohashes(
            geohashes=geohashes,
            largest_gh_size=4,
            smallest_gh_size=6,
            gh_input_level=5
        )
        
        assert isinstance(result, list)
        assert len(result) == 1
        # Single geohash can't be optimized without siblings, should remain unchanged
        assert result[0] == 'tdr1y'
        
    def test_basic_optimization(self):
        """Test basic optimization with geohashes that can be combined."""
        # Create a complete set of child geohashes that should combine into parent
        base = 'tdr1'
        geohashes = [base + char for char in BASE32]
        
        result = get_optimized_geohashes(
            geohashes=geohashes,
            largest_gh_size=4,
            smallest_gh_size=6,
            gh_input_level=5,
            percentage_error=10
        )
        
        assert isinstance(result, list)
        assert len(result) == 1
        assert result[0] == base
        
    def test_partial_optimization(self):
        """Test optimization with partial set of child geohashes."""
        # Create partial set that shouldn't be optimized
        base = 'tdr1'
        geohashes = [base + char for char in BASE32[:10]]  # Only first 10 children
        
        result = get_optimized_geohashes(
            geohashes=geohashes,
            largest_gh_size=4,
            smallest_gh_size=6,
            gh_input_level=5,
            percentage_error=10
        )
        
        assert isinstance(result, list)
        assert len(result) == 10  # Should remain unoptimized
        
    def test_optimization_with_error_threshold(self):
        """Test optimization respects percentage error threshold."""
        base = 'tdr1'
        # Create 29 out of 32 children (90.6% coverage)
        geohashes = [base + char for char in BASE32[:29]]
        
        # With 10% error threshold, this should optimize
        result_10_percent = get_optimized_geohashes(
            geohashes=geohashes,
            largest_gh_size=4,
            smallest_gh_size=6,
            gh_input_level=5,
            percentage_error=10
        )
        
        # With 5% error threshold, this should not optimize
        result_5_percent = get_optimized_geohashes(
            geohashes=geohashes,
            largest_gh_size=4,
            smallest_gh_size=6,
            gh_input_level=5,
            percentage_error=5
        )
        
        assert isinstance(result_10_percent, list)
        assert isinstance(result_5_percent, list)
        assert len(result_10_percent) < len(result_5_percent)
        
    def test_forced_upscale(self):
        """Test forced upscale functionality."""
        # Use geohashes longer than smallest_gh_size
        geohashes = ['tdr1y123', 'tdr1z456', 'tdr20789']
        
        result_no_force = get_optimized_geohashes(
            geohashes=geohashes,
            largest_gh_size=4,
            smallest_gh_size=6,
            gh_input_level=8,
            forced_gh_upscale=False
        )
        
        result_with_force = get_optimized_geohashes(
            geohashes=geohashes,
            largest_gh_size=4,
            smallest_gh_size=6,
            gh_input_level=8,
            forced_gh_upscale=True
        )
        
        assert isinstance(result_no_force, list)
        assert isinstance(result_with_force, list)
        
        # With forced upscale, geohashes should be truncated to smallest_gh_size
        for gh in result_with_force:
            assert len(gh) <= 6
            
    def test_different_precision_levels(self):
        """Test optimization with different precision level parameters."""
        geohashes = ['tdr1y', 'tdr1z', 'tdr20', 'tdr21']
        
        # Test with different largest_gh_size values
        result_large_4 = get_optimized_geohashes(
            geohashes=geohashes,
            largest_gh_size=4,
            smallest_gh_size=6,
            gh_input_level=5
        )
        
        result_large_3 = get_optimized_geohashes(
            geohashes=geohashes,
            largest_gh_size=3,
            smallest_gh_size=6,
            gh_input_level=5
        )
        
        assert isinstance(result_large_4, list)
        assert isinstance(result_large_3, list)
        
        # More aggressive optimization (smaller largest_gh_size) should result in fewer geohashes
        assert len(result_large_3) <= len(result_large_4)
        
    def test_optimization_cycles(self):
        """Test that optimization runs multiple cycles when needed."""
        # Create nested structure that requires multiple optimization cycles
        base1 = 'tdr1'
        base2 = 'tdr2'
        
        # Create complete sets for two different base geohashes
        geohashes = []
        geohashes.extend([base1 + char for char in BASE32])
        geohashes.extend([base2 + char for char in BASE32])
        
        result = get_optimized_geohashes(
            geohashes=geohashes,
            largest_gh_size=3,  # Should optimize to 'tdr'
            smallest_gh_size=6,
            gh_input_level=5
        )
        
        assert isinstance(result, list)
        # Should optimize both sets and potentially combine further
        assert len(result) <= 2
        
    def test_mixed_precision_input(self):
        """Test optimization with mixed precision input geohashes."""
        geohashes = [
            'tdr1',      # 4 chars
            'tdr1y',     # 5 chars  
            'tdr1z123',  # 8 chars
            'tdr20',     # 5 chars
        ]
        
        result = get_optimized_geohashes(
            geohashes=geohashes,
            largest_gh_size=4,
            smallest_gh_size=6,
            gh_input_level=5
        )
        
        assert isinstance(result, list)
        assert len(result) > 0
        
        # All results should be valid geohash strings
        for gh in result:
            assert isinstance(gh, str)
            assert len(gh) >= 3  # Reasonable minimum length
            
    def test_optimization_preserves_coverage(self):
        """Test that optimization preserves geographic coverage."""
        # Use geohashes that represent different geographic areas
        geohashes = [
            'tdr1y0', 'tdr1y1', 'tdr1y2', 'tdr1y3',  # Can be optimized to 'tdr1y'
            'tdr2x0', 'tdr2x1'  # Different area, partial set
        ]
        
        result = get_optimized_geohashes(
            geohashes=geohashes,
            largest_gh_size=4,
            smallest_gh_size=7,
            gh_input_level=6
        )
        
        assert isinstance(result, list)
        assert len(result) > 0
        
        # Should contain optimized version of first group and preserve second group
        optimized_geohashes = set(result)
        assert 'tdr1y' in optimized_geohashes or any(gh.startswith('tdr1y') for gh in result)
        assert any(gh.startswith('tdr2x') for gh in result)
        
    def test_edge_case_single_character_geohash(self):
        """Test optimization with single character geohashes."""
        geohashes = ['t', 'd', 'r']
        
        result = get_optimized_geohashes(
            geohashes=geohashes,
            largest_gh_size=1,
            smallest_gh_size=3,
            gh_input_level=1
        )
        
        assert isinstance(result, list)
        assert len(result) == 3  # Should remain unchanged
        assert set(result) == set(geohashes)
        
    def test_optimization_with_duplicates(self):
        """Test optimization handles duplicate geohashes correctly."""
        geohashes = ['tdr1y', 'tdr1y', 'tdr1z', 'tdr1z', 'tdr20']
        
        result = get_optimized_geohashes(
            geohashes=geohashes,
            largest_gh_size=4,
            smallest_gh_size=6,
            gh_input_level=5
        )
        
        assert isinstance(result, list)
        # Should handle duplicates (function uses set internally)
        unique_result = set(result)
        assert len(unique_result) <= 3  # At most 3 unique geohashes
        
    def test_boundary_conditions(self):
        """Test optimization with boundary condition parameters."""
        geohashes = ['tdr1y', 'tdr1z', 'tdr20']
        
        # Test when largest_gh_size equals smallest_gh_size
        result_equal = get_optimized_geohashes(
            geohashes=geohashes,
            largest_gh_size=5,
            smallest_gh_size=5,
            gh_input_level=5
        )
        
        # Test when gh_input_level equals largest_gh_size
        result_input_equal = get_optimized_geohashes(
            geohashes=geohashes,
            largest_gh_size=5,
            smallest_gh_size=6,
            gh_input_level=5
        )
        
        assert isinstance(result_equal, list)
        assert isinstance(result_input_equal, list)
        
        # Both should return valid results
        assert len(result_equal) > 0
        assert len(result_input_equal) > 0
        
    def test_large_geohash_set(self):
        """Test optimization performance with larger geohash sets."""
        # Create a larger set of geohashes for performance testing
        base_geohashes = ['tdr1', 'tdr2', 'tdr3', 'tdr4']
        geohashes = []
        
        for base in base_geohashes:
            # Add some children for each base
            geohashes.extend([base + char for char in BASE32[:8]])
            
        result = get_optimized_geohashes(
            geohashes=geohashes,
            largest_gh_size=3,
            smallest_gh_size=6,
            gh_input_level=5
        )
        
        assert isinstance(result, list)
        assert len(result) > 0
        # With partial sets (8 out of 32 children), optimization may not occur
        # Just verify we get a valid result
        assert len(result) <= len(geohashes)  # Should not increase the count
        
    def test_no_optimization_possible(self):
        """Test case where no optimization is possible."""
        # Use geohashes that are already at largest_gh_size and can't be combined
        geohashes = ['tdr1', 'xyz9', 'abc5']  # Different prefixes, can't combine
        
        result = get_optimized_geohashes(
            geohashes=geohashes,
            largest_gh_size=4,
            smallest_gh_size=6,
            gh_input_level=4
        )
        
        assert isinstance(result, list)
        assert len(result) == 3  # Should remain unchanged
        assert set(result) == set(geohashes)
        
    def test_return_type_consistency(self):
        """Test that function always returns consistent types."""
        test_cases = [
            [],  # Empty list
            ['tdr1y'],  # Single geohash
            ['tdr1y', 'tdr1z'],  # Multiple geohashes
        ]
        
        for geohashes in test_cases:
            result = get_optimized_geohashes(
                geohashes=geohashes,
                largest_gh_size=4,
                smallest_gh_size=6,
                gh_input_level=5
            )
            
            if geohashes:  # Non-empty input
                assert isinstance(result, list)
                for item in result:
                    assert isinstance(item, str)
            else:  # Empty input
                assert result is False