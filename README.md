# polygeohaser

polygeoasher is a python package to implement polygon to geohash and vice versa with optimisation of geohash levels as per the user requirement, with error rate being controlled by the user. 

## Installation

Use the package manager [pip](https://pip.pypa.io/en/stable/) to install polygeohasher.

```bash
pip install polygeohasher

#install all dependencies
pip3 install -r requirements.txt

```

## Usage

```python
import polygeohasher
import geopandas as gpd

gdf = gpd.read_file("your geospatial file format") # read your geometry file here

primary_df = polygeohasher.create_geohash_list(gdf, geohash_level,inner=False) # returns a dataframe with list of geohashes for each geometry

secondary_df = polygeohasher.polygon_geohash_level(primary_df, largest_gh_size, smallest_gh_size, gh_input_level) # returns optimised list of geohash 

polygeohasher.optimization_summary(primary_df, secondary_df) #creates a summary of first and second output

'''
--------------------------------------------------
            OPTIMIZATION SUMMARY
--------------------------------------------------
Total Counts of Initial Geohashes :  2597
Total Counts of Final Geohashes   :  837
Percent of optimization           :  67.77 %
--------------------------------------------------
'''

geo_df = polygeohasher.geohashes_to_geometry(secondary_df) # return geometry for a DataFrame with a column - `opitimized_geohash_list` (output from above)

geo_df.to_file("your write path.format",driver = "GeoJSON") #write file in your favorite spatial file format

```

## Contributing
Pull requests are welcome. For major changes, please open an issue first to discuss what you would like to change.

Please make sure to update tests as appropriate.

## License
[Apache License, Version 2.0](http://www.apache.org/licenses/LICENSE-2.0)