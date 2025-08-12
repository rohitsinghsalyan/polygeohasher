# Design Document

## Overview

This design document outlines the reorganization of the polygeohasher package to create a clean, consistent, and maintainable codebase. The refactoring will establish clear module boundaries, provide both functional and class-based APIs, improve testing structure, and ensure documentation accuracy.

## Architecture

### Current Structure Issues
- Mixed API paradigms (class-based implementation with functional documentation)
- Circular import patterns between modules
- Inconsistent function organization
- Duplicate test function names
- Unclear public API boundaries

### Target Structure
```
polygeohasher/
├── __init__.py           # Public API exports
├── core.py              # Core functionality (functional API)
├── polygeohasher.py     # Class-based API (refactored)
├── converters.py        # Geohash/polygon conversion utilities
└── utils.py             # Helper functions and constants
```

## Components and Interfaces

### 1. Public API Module (`__init__.py`)
**Purpose**: Expose clean public API with both functional and class-based interfaces

**Exports**:
- Functional API: `create_geohash_list()`, `geohash_optimizer()`, `geohashes_to_geometry()`, `optimization_summary()`
- Class-based API: `Polygeohasher` class
- Version information

### 2. Core Module (`core.py`)
**Purpose**: Implement core functionality as standalone functions

**Functions**:
- `create_geohash_list(gdf, geohash_level, inner=False)` - Convert geometries to geohashes
- `geohash_optimizer(gdf_with_geohashes, largest_gh_size, smallest_gh_size, gh_input_level, **kwargs)` - Optimize geohash levels
- `geohashes_to_geometry(df, geohash_column_name)` - Convert geohashes back to geometries
- `optimization_summary(initial_gdf, final_gdf)` - Print optimization statistics

### 3. Polygeohasher Class (`polygeohasher.py`)
**Purpose**: Provide object-oriented interface wrapping core functions

**Methods**:
- `__init__(self, gdf)` - Initialize with GeoDataFrame
- `create_geohash_list(self, geohash_level, inner=False)` - Instance method wrapper
- `geohash_optimizer(self, gdf_with_geohashes, **kwargs)` - Instance method wrapper
- `geohashes_to_geometry(self, df, geohash_column_name)` - Static method wrapper
- `optimization_summary(self, initial_gdf, final_gdf)` - Static method wrapper

### 4. Converters Module (`converters.py`)
**Purpose**: Handle low-level geohash/polygon conversions

**Functions**:
- `geohash_to_polygon(geo)` - Convert single geohash to polygon
- `polygon_to_geohashes(polygon, precision, inner=True)` - Convert polygon to geohashes
- `geohashes_to_polygon(geohashes)` - Convert multiple geohashes to unified polygon

### 5. Utils Module (`utils.py`)
**Purpose**: Shared utilities and constants

**Contents**:
- `BASE32` constant for geohash characters
- `get_optimized_geohashes()` - Core optimization algorithm
- Helper functions for geohash manipulation

## Data Models

### Input Data Models
- **GeoDataFrame**: Standard geopandas GeoDataFrame with geometry column
- **Geohash Lists**: Lists of geohash strings associated with geometries
- **Configuration Parameters**: Precision levels, error thresholds, optimization flags

### Output Data Models
- **Geohash DataFrame**: DataFrame with geohash_list column
- **Optimized DataFrame**: DataFrame with optimized_geohash_list column
- **Geometry DataFrame**: GeoDataFrame with reconstructed geometries

## Error Handling

### Input Validation
- Validate GeoDataFrame structure and geometry column presence
- Check geohash precision level ranges (1-12)
- Validate optimization parameters (error percentages, size constraints)

### Error Types
- `ValueError`: Invalid input parameters or data structure
- `TypeError`: Incorrect data types for function arguments
- `AttributeError`: Missing required DataFrame columns

### Error Recovery
- Graceful handling of empty geometry collections
- Default parameter fallbacks for optional arguments
- Clear error messages with suggested fixes

## Testing Strategy

### Test Organization
```
tests/
├── __init__.py
├── test_core.py              # Test functional API
├── test_polygeohasher.py     # Test class-based API
├── test_converters.py        # Test conversion utilities
├── test_utils.py             # Test utility functions
└── fixtures/
    ├── __init__.py
    └── sample_data.py        # Shared test data
```

### Test Categories
1. **Unit Tests**: Individual function testing with mocked dependencies
2. **Integration Tests**: End-to-end workflow testing
3. **API Consistency Tests**: Ensure functional and class APIs produce identical results
4. **Edge Case Tests**: Empty inputs, boundary conditions, error scenarios

### Test Data Management
- Centralized test fixtures in `fixtures/sample_data.py`
- Consistent test data across all test modules
- Parameterized tests for different input scenarios

## Implementation Approach

### Phase 1: Module Separation
1. Extract conversion functions to `converters.py`
2. Move optimization algorithm to `utils.py`
3. Create functional API in `core.py`

### Phase 2: API Consistency
1. Refactor class methods to use core functions
2. Ensure identical behavior between functional and class APIs
3. Update `__init__.py` to expose both APIs

### Phase 3: Testing Refactor
1. Reorganize tests by module
2. Fix duplicate function names
3. Add comprehensive test coverage

### Phase 4: Documentation Update
1. Update README with both API examples
2. Add docstrings to all public functions
3. Ensure example code works with new structure