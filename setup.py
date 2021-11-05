import setuptools

with open("README.md", "r") as fh:
    long_description = fh.read()

setuptools.setup(
    name="polygeohasher",
    version="0.0.5",
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
    install_requires=["Geohash", "geopandas", "polygon-geohasher"],
    python_requires=">=3.6",
)
