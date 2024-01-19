import geopandas as gpd
from polygeohasher import polygeohasher
import pytest

@pytest.fixture
def gdf():
    gdf = gpd.read_file("example/sample.geojson")
    return gdf

@pytest.fixture
def pgh(gdf):
    pgh = polygeohasher.Polygeohasher(gdf)
    return pgh

@pytest.fixture
def initial_df(pgh):
    initial_df = pgh.create_geohash_list(6)
    return initial_df

@pytest.fixture
def final_df(pgh, initial_df):
    final_df = pgh.geohash_optimizer(initial_df, 5, 7, 6) 
    return final_df

def test_polygeohasher_init(gdf, pgh):
    assert gdf.empty !=True
    assert pgh != None

def test_create_geohash_list(initial_df):
    assert len(initial_df["geohash_list"]) == 4
    
def test_create_geohash_list(initial_df, final_df):
    assert sum([len(i) for i in initial_df["geohash_list"]]) == 2597
    assert len(final_df) == 837
    
def test_geohashes_to_geometry(pgh, final_df):
    geom = pgh.geohashes_to_geometry(final_df)
    assert ("geometry" in list(geom.columns))== True
