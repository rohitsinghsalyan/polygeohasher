import geopandas as gpd
import pandas as pd
from polygeohasher import polygeohasher, core
from tests.fixtures.sample_data import sample_gdf, simple_polygon_gdf, geohash_dataframe
import pytest


@pytest.fixture
def pgh(sample_gdf):
    """Create Polygeohasher instance with sample data."""
    return polygeohasher.Polygeohasher(sample_gdf)


@pytest.fixture
def initial_df(pgh):
    """Create initial geohash DataFrame using class method."""
    return pgh.create_geohash_list(6)


@pytest.fixture
def final_df(pgh, initial_df):
    """Create optimized geohash DataFrame using class method."""
    return pgh.geohash_optimizer(initial_df, 5, 7, 6)


# Class-based API tests
def test_polygeohasher_init(sample_gdf, pgh):
    """Test Polygeohasher class initialization."""
    assert not sample_gdf.empty
    assert pgh is not None
    assert pgh.gdf.equals(sample_gdf)


def test_class_create_geohash_list_basic(initial_df):
    """Test basic functionality of class create_geohash_list method."""
    assert len(initial_df["geohash_list"]) == 4
    assert "geohash_list" in initial_df.columns
    assert all(isinstance(gh_list, list) for gh_list in initial_df["geohash_list"])


def test_class_create_geohash_list_counts(initial_df, final_df):
    """Test geohash counts from class methods."""
    assert sum([len(i) for i in initial_df["geohash_list"]]) == 2597
    assert len(final_df) == 837


def test_class_geohashes_to_geometry(pgh, final_df):
    """Test class geohashes_to_geometry method."""
    geom = pgh.geohashes_to_geometry(final_df)
    assert "geometry" in list(geom.columns)
    assert isinstance(geom, gpd.GeoDataFrame)


def test_class_optimization_summary(pgh, initial_df, final_df, capsys):
    """Test class optimization_summary method."""
    pgh.optimization_summary(initial_df, final_df)
    captured = capsys.readouterr()
    assert "OPTIMIZATION SUMMARY" in captured.out
    assert "Total Counts of Initial Geohashes" in captured.out
    assert "Total Counts of Final Geohashes" in captured.out


# API Consistency tests - ensure functional and class APIs produce identical results
def test_api_consistency_create_geohash_list(simple_polygon_gdf):
    """Test that functional and class APIs produce identical results for create_geohash_list."""
    # Class-based API
    pgh = polygeohasher.Polygeohasher(simple_polygon_gdf)
    class_result = pgh.create_geohash_list(4)
    
    # Functional API
    functional_result = core.create_geohash_list(simple_polygon_gdf, 4)
    
    # Compare results
    pd.testing.assert_frame_equal(class_result, functional_result)


def test_api_consistency_create_geohash_list_with_inner(simple_polygon_gdf):
    """Test API consistency for create_geohash_list with inner parameter."""
    # Class-based API
    pgh = polygeohasher.Polygeohasher(simple_polygon_gdf)
    class_result = pgh.create_geohash_list(4, inner=True)
    
    # Functional API
    functional_result = core.create_geohash_list(simple_polygon_gdf, 4, inner=True)
    
    # Compare results
    pd.testing.assert_frame_equal(class_result, functional_result)


def test_api_consistency_geohash_optimizer(geohash_dataframe):
    """Test that functional and class APIs produce identical results for geohash_optimizer."""
    # Class-based API (note: class method doesn't use self.gdf for this operation)
    pgh = polygeohasher.Polygeohasher(gpd.GeoDataFrame())  # Empty GDF since not used
    class_result = pgh.geohash_optimizer(geohash_dataframe, 4, 6, 5)
    
    # Functional API
    functional_result = core.geohash_optimizer(geohash_dataframe, 4, 6, 5)
    
    # Compare results
    pd.testing.assert_frame_equal(class_result, functional_result)


def test_api_consistency_geohash_optimizer_with_params(geohash_dataframe):
    """Test API consistency for geohash_optimizer with optional parameters."""
    # Class-based API
    pgh = polygeohasher.Polygeohasher(gpd.GeoDataFrame())
    class_result = pgh.geohash_optimizer(
        geohash_dataframe, 4, 6, 5, 
        percentage_error=15, 
        forced_gh_upscale=True
    )
    
    # Functional API
    functional_result = core.geohash_optimizer(
        geohash_dataframe, 4, 6, 5,
        percentage_error=15,
        forced_gh_upscale=True
    )
    
    # Compare results
    pd.testing.assert_frame_equal(class_result, functional_result)


def test_api_consistency_geohashes_to_geometry():
    """Test that functional and class APIs produce identical results for geohashes_to_geometry."""
    # Create test data
    test_df = pd.DataFrame({
        'optimized_geohash_list': ['tdr1y', 'tdr1z', 'tdr20']
    })
    
    # Class-based API
    pgh = polygeohasher.Polygeohasher(gpd.GeoDataFrame())
    class_result = pgh.geohashes_to_geometry(test_df)
    
    # Functional API
    functional_result = core.geohashes_to_geometry(test_df)
    
    # Compare results
    assert class_result.equals(functional_result)
    assert isinstance(class_result, gpd.GeoDataFrame)
    assert isinstance(functional_result, gpd.GeoDataFrame)


def test_api_consistency_geohashes_to_geometry_custom_column():
    """Test API consistency for geohashes_to_geometry with custom column name."""
    # Create test data
    test_df = pd.DataFrame({
        'custom_geohash_col': ['tdr1y', 'tdr1z', 'tdr20']
    })
    
    # Class-based API
    pgh = polygeohasher.Polygeohasher(gpd.GeoDataFrame())
    class_result = pgh.geohashes_to_geometry(test_df, 'custom_geohash_col')
    
    # Functional API
    functional_result = core.geohashes_to_geometry(test_df, 'custom_geohash_col')
    
    # Compare results
    assert class_result.equals(functional_result)


def test_api_consistency_optimization_summary(capsys):
    """Test that functional and class APIs produce identical output for optimization_summary."""
    # Create test data
    initial_df = pd.DataFrame({
        'geohash_list': [['a', 'b', 'c', 'd'], ['e', 'f']]
    })
    final_df = pd.DataFrame({
        'optimized_geohash_list': ['ab', 'ef']
    })
    
    # Class-based API
    pgh = polygeohasher.Polygeohasher(gpd.GeoDataFrame())
    pgh.optimization_summary(initial_df, final_df)
    class_output = capsys.readouterr().out
    
    # Functional API
    core.optimization_summary(initial_df, final_df)
    functional_output = capsys.readouterr().out
    
    # Compare outputs
    assert class_output == functional_output
    assert "OPTIMIZATION SUMMARY" in class_output


# Class method wrapper tests
def test_class_method_wrappers_preserve_signatures(simple_polygon_gdf):
    """Test that class method wrappers preserve function signatures and behavior."""
    pgh = polygeohasher.Polygeohasher(simple_polygon_gdf)
    
    # Test create_geohash_list wrapper with lower geohash levels for speed
    result1 = pgh.create_geohash_list(4)
    result2 = pgh.create_geohash_list(4, inner=False)
    result3 = pgh.create_geohash_list(4, inner=True)
    
    assert isinstance(result1, pd.DataFrame)
    assert isinstance(result2, pd.DataFrame)
    assert isinstance(result3, pd.DataFrame)
    assert "geohash_list" in result1.columns
    
    # Results with different inner parameter should be different
    assert not result2.equals(result3)


def test_class_method_error_handling(simple_polygon_gdf):
    """Test that class methods handle errors appropriately."""
    pgh = polygeohasher.Polygeohasher(simple_polygon_gdf)
    
    # Test invalid DataFrame for optimizer (this is a more reliable test)
    with pytest.raises((KeyError, AttributeError)):
        invalid_df = pd.DataFrame({'wrong_column': [1, 2, 3]})
        pgh.geohash_optimizer(invalid_df, 3, 5, 4)
    
    # Test invalid column name for geohashes_to_geometry
    with pytest.raises((KeyError, AttributeError)):
        invalid_df = pd.DataFrame({'wrong_column': ['abc123']})
        pgh.geohashes_to_geometry(invalid_df, 'nonexistent_column')


def test_class_maintains_state(sample_gdf):
    """Test that Polygeohasher class maintains its state correctly."""
    pgh = polygeohasher.Polygeohasher(sample_gdf)
    
    # Original GDF should be preserved
    assert pgh.gdf.equals(sample_gdf)
    
    # Operations should not modify the original GDF
    result = pgh.create_geohash_list(6)
    assert pgh.gdf.equals(sample_gdf)  # Should be unchanged
    assert "geohash_list" not in pgh.gdf.columns  # Original should not be modified
