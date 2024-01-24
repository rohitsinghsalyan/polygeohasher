# polygeohasher

polygeohasher is a python package to implement polygon to geohash and vice versa with optimisation of geohash levels as per the user requirement, with error rate being controlled by the user.

## Installation

Use the package manager [pip](https://pip.pypa.io/en/stable/) to install polygeohasher.

```bash
pip3 install polygeohasher
```
Poetry: Add package to lock file
```bash
poetry add polygeohasher
```
## Usage

```python
from polygeohasher import polygeohasher
import geopandas as gpd

# read geojson(geometry) file
gdf = gpd.read_file("your geospatial file format") # read your geometry file here

# initialize polygeohasher
pgh = polygeohasher.Polygeohasher(gdf)

# declare geohash levels
INPUT_GEOHASH_LEVEL = 6
MINIMUM_GEOHASH_LEVEL = 5
MAXIMUM_GEOHASH_LEVEL = 7

# create a dataframe with list of geohashes for each geometry
initial_df = pgh.create_geohash_list(INPUT_GEOHASH_LEVEL,inner=False)

# get a dataframe with optimized list of geohashes
final_df = pgh.geohash_optimizer(initial_df, MINIMUM_GEOHASH_LEVEL, MAXIMUM_GEOHASH_LEVEL, INPUT_GEOHASH_LEVEL) 

# prints optimization summary
pgh.optimization_summary(initial_df, final_df)

# convert geohash to geometry
geo_df = pgh.geohashes_to_geometry(final_df, "geohash_column_name")

# write file in desired spatial file format
geo_df.to_file("your write path.format",driver = "GeoJSON") 

```
Following is the optimization summary:
```bash
--------------------------------------------------
            OPTIMIZATION SUMMARY
--------------------------------------------------
Total Counts of Initial Geohashes :  2597
Total Counts of Final Geohashes   :  837
Percent of optimization           :  67.77 %
--------------------------------------------------
```

## Some visualisations

<img src="example/study_area.png" alt="study_area" width="100%"/>

Study are consist of division of City of Bengaluru in India.

<img src="example/primary_output.png" alt="primary_output" width="100%"/>

Primary Output of geohashes without any optimisation.

<img src="example/secondary_output.png" alt="secondary_output" width="100%"/>

Final Output of geohashes with optimization of number of geohashes at different levels to cover an area.


## Contributing
Pull requests are welcome. For major changes, please open an issue first to discuss what you would like to change.

Please make sure to update tests as appropriate.

## License
[Apache License, Version 2.0](http://www.apache.org/licenses/LICENSE-2.0)
