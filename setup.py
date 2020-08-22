import setuptools

with open("README.md", "r") as fh:
    long_description = fh.read()

setuptools.setup(
    name="polygeohasher-rohitsinghsalyan",
    version="0.0.1",
    author="Rohit Singh, Krishna Khadka",
    author_email="rohitsinghsalyan@gmail.com",
    description="Convert your polygons into a set of geohashes with min and max resoulution set by users",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/rohitsinghsalyan/polygeohasher",
    packages=setuptools.find_packages(),
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: Apache Software License",
        "Operating System :: OS Independent",
    ],
    install_requires=[
          'Fiona>=1.8.13.post1',
          'Geohash>=1.0',
          'geopandas>=0.8.1',
          'numpy>=1.19.1',
          'pandas>=1.1.0',
          'polygon-geohasher>=0.0.1',
          'pyproj>=2.6.1',
          'python-geohash>=0.8.5',
          'Shapely>=1.7.0'
      ],
    python_requires='>=3.6',
)


