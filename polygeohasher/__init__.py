"""
Polygeohasher: A complete package to work with polygons and geohashes.

This package provides both functional and class-based APIs for:
- Converting polygons to geohashes
- Optimizing geohash levels to cover areas with controlled error percentage
- Converting geohashes back to polygons for visualization

Functional API:
    - create_geohash_list()
    - geohash_optimizer()
    - geohashes_to_geometry()
    - optimization_summary()

Class-based API:
    - Polygeohasher class
"""

__version__ = "1.1.0"

# Import core functional API
from .core import (
    create_geohash_list,
    geohash_optimizer,
    geohashes_to_geometry,
    optimization_summary,
)

# Import class-based API
from .polygeohasher import Polygeohasher

# Define public API
__all__ = [
    # Functional API
    "create_geohash_list",
    "geohash_optimizer", 
    "geohashes_to_geometry",
    "optimization_summary",
    # Class-based API
    "Polygeohasher",
    # Version
    "__version__",
]
