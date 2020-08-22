# polygeohaser

polygeoasher is a python package to implement polygon to geohash and vice versa with optimisation of geohash levels as per the user requirement, with error rate being controlled by the user. 

## Installation

Use the package manager [pip](https://pip.pypa.io/en/stable/) to install foobar.

```bash
pip install polygeohasher
```

## Usage

```python
import polygeohasher

polygeohasher.create_geohash_list(GeoDataFrame, geohash_level,inner=False) # returns a dataframe with list of geohashes for each geometry
polygon_geohash_level(GeoDataFrame, largest_gh_size, smallest_gh_size, gh_input_level) # returns optimised list of geohash 
optimization_summary(initial_gdf, final_gdf) #creates a summary of first and second output
geohashes_to_geometry(df) # return geometry for a DataFrame with a column - `opitimized_geohash_list` (output from above)
```

## Contributing
Pull requests are welcome. For major changes, please open an issue first to discuss what you would like to change.

Please make sure to update tests as appropriate.

## License
[Apache License, Version 2.0](http://www.apache.org/licenses/LICENSE-2.0)