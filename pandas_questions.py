"""Plotting referendum results in pandas.

In short, we want to make beautiful map to report results of a referendum. In
some way, we would like to depict results with something similar to the maps
that you can find here:
https://github.com/x-datascience-datacamp/datacamp-assignment-pandas/blob/main/example_map.png

To do that, you will load the data as pandas.DataFrame, merge the info and
aggregate them by regions and finally plot them on a map using `geopandas`.
"""
import pandas as pd
import geopandas as gpd
import matplotlib.pyplot as plt



def load_data():
    """Load data from the CSV files."""
    referendum = pd.read_csv("data/referendum.csv", sep=";")
    regions = pd.read_csv("data/regions.csv")
    departments = pd.read_csv("data/departments.csv")

    return referendum, regions, departments


def merge_regions_and_departments(regions, departments):
    """Merge regions and departments in one DataFrame."""
    regions = regions.rename(
        columns={"code": "code_reg", "name": "name_reg"}
    )
    departments = departments.rename(
        columns={"code": "code_dep", "name": "name_dep"}
    )

    merged = departments.merge(
        regions,
        left_on="region_code",
        right_on="code_reg",
        how="inner"
    )

    return merged[["code_reg", "name_reg", "code_dep", "name_dep"]]


def merge_referendum_and_areas(referendum, regions_and_departments):
    """Merge referendum results with geographical information."""
    referendum = referendum.copy()
    referendum["Department code"] = (
        referendum["Department code"].astype(str).str.zfill(2)
    )

    referendum = referendum[
        ~referendum["Department code"].str.contains("Z")
    ]

    merged = referendum.merge(
        regions_and_departments,
        left_on="Department code",
        right_on="code_dep",
        how="inner"
    )

    return merged


def compute_referendum_result_by_regions(referendum_and_areas):
    """Compute referendum results for each region."""
    columns_to_sum = [
        "Registered",
        "Abstentions",
        "Null",
        "Choice A",
        "Choice B"
    ]

    result = referendum_and_areas.groupby("code_reg").agg(
        name_reg=("name_reg", "first"),
        **{
            col: (col, "sum")
            for col in columns_to_sum
        }
    )

    return result


def plot_referendum_map(referendum_result_by_regions):
    """Plot referendum results on a map."""
    regions = gpd.read_file("data/regions.geojson")

    results = referendum_result_by_regions.reset_index()

    gdf = regions.merge(
        results,
        left_on="code",
        right_on="code_reg",
        how="inner"
    )

    gdf["ratio"] = (
        gdf["Choice A"] /
        (gdf["Choice A"] + gdf["Choice B"])
    )

    gdf.plot(
        column="ratio",
        cmap="RdYlGn",
        legend=True,
        edgecolor="black",
        figsize=(12, 8)
    )

    plt.title("Referendum results by region")
    plt.axis("off")

    return gdf
