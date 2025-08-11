"""
Geohash and polygon conversion utilities.

This module provides functions for converting between geohashes and polygon geometries,
enabling bidirectional conversion for spatial data processing.
"""

import geohash
import queue
from typing import Set, List, Union, Any

from shapely import geometry
from shapely.ops import unary_union
from shapely.geometry import Polygon


def geohash_to_polygon(geo: str) -> Polygon:
    """
    Convert a geohash string to a Shapely Polygon.
    
    Args:
        geo: String that represents the geohash.
        
    Returns:
        A Shapely Polygon instance that represents the geohash bounding box.
        
    Example:
        >>> polygon = geohash_to_polygon("9q8yy")
        >>> isinstance(polygon, Polygon)
        True
    """
    lat_centroid, lng_centroid, lat_offset, lng_offset = geohash.decode_exactly(geo)

    corner_1 = (lat_centroid - lat_offset, lng_centroid - lng_offset)[::-1]
    corner_2 = (lat_centroid - lat_offset, lng_centroid + lng_offset)[::-1]
    corner_3 = (lat_centroid + lat_offset, lng_centroid + lng_offset)[::-1]
    corner_4 = (lat_centroid + lat_offset, lng_centroid - lng_offset)[::-1]

    return geometry.Polygon([corner_1, corner_2, corner_3, corner_4, corner_1])


def polygon_to_geohashes(polygon: Polygon, precision: int, inner: bool = True) -> Set[str]:
    """
    Convert a Shapely polygon to a set of geohashes that cover the polygon area.
    
    Args:
        polygon: Shapely polygon to convert.
        precision: Geohash precision level (1-12). Higher values provide more detail.
        inner: If True, only include geohashes completely inside the polygon.
               If False, include geohashes that intersect with the polygon.
               
    Returns:
        Set of geohash strings that form the polygon coverage.
        
    Example:
        >>> from shapely.geometry import Polygon
        >>> poly = Polygon([(0, 0), (1, 0), (1, 1), (0, 1)])
        >>> geohashes = polygon_to_geohashes(poly, 5)
        >>> isinstance(geohashes, set)
        True
    """
    inner_geohashes = set()
    outer_geohashes = set()

    envelope = polygon.envelope
    centroid = polygon.centroid

    testing_geohashes: queue.Queue[str] = queue.Queue()
    testing_geohashes.put(geohash.encode(centroid.y, centroid.x, precision))

    while not testing_geohashes.empty():
        current_geohash = testing_geohashes.get()

        if (
            current_geohash not in inner_geohashes
            and current_geohash not in outer_geohashes
        ):
            current_polygon = geohash_to_polygon(current_geohash)

            condition = (
                envelope.contains(current_polygon)
                if inner
                else envelope.intersects(current_polygon)
            )

            if condition:
                if inner:
                    if polygon.contains(current_polygon):
                        inner_geohashes.add(current_geohash)
                    else:
                        outer_geohashes.add(current_geohash)
                else:
                    if polygon.intersects(current_polygon):
                        inner_geohashes.add(current_geohash)
                    else:
                        outer_geohashes.add(current_geohash)
                for neighbor in geohash.neighbors(current_geohash):
                    if (
                        neighbor not in inner_geohashes
                        and neighbor not in outer_geohashes
                    ):
                        testing_geohashes.put(neighbor)

    return inner_geohashes


def geohashes_to_polygon(geohashes: List[str]) -> Union[Polygon, geometry.MultiPolygon]:
    """
    Convert a list of geohashes to a unified Shapely geometry.
    
    Args:
        geohashes: List of geohash strings to combine into a single geometry.
        
    Returns:
        Shapely geometry (Polygon or MultiPolygon) representing the union of all geohashes.
        
    Example:
        >>> geohashes = ["9q8yy", "9q8yz"]
        >>> result = geohashes_to_polygon(geohashes)
        >>> hasattr(result, 'area')
        True
    """
    return unary_union([geohash_to_polygon(g) for g in geohashes])