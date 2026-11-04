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
    """Load data from the CSV files referundum/regions/departments."""
    referendum = pd.read_csv("data/referendum.csv", sep=";")
    regions = pd.read_csv("data/regions.csv")
    departments = pd.read_csv("data/departments.csv")

    return referendum, regions, departments


def merge_regions_and_departments(regions, departments):
    """Merge regions and departments in one DataFrame.

    The columns in the final DataFrame should be:
    ['code_reg', 'name_reg', 'code_dep', 'name_dep']
    """
    regions = regions.rename(
        columns={"code": "code_reg", "name": "name_reg"}
    )
    departments = departments.rename(
        columns={
            "region_code": "code_reg",
            "code": "code_dep",
            "name": "name_dep",
        }
    )

    regions_and_departments = pd.merge(
        regions[["code_reg", "name_reg"]],
        departments[["code_reg", "code_dep", "name_dep"]],
        on="code_reg",
        how="inner",
    )

    return regions_and_departments


def merge_referendum_and_areas(referendum, regions_and_departments):
    """Merge referendum and regions_and_departments in one DataFrame.

    You can drop the lines relative to DOM-TOM-COM departments, and the
    french living abroad, which all have a code that contains `Z`.

    DOM-TOM-COM departments are departements that are remote from metropolitan
    France, like Guadaloupe, Reunion, or Tahiti.
    """
    referendum = referendum.copy()
    referendum["Department code"] = (
        referendum["Department code"].astype(str).str.zfill(2)
    )
    referendum = referendum[~referendum["Department code"].str.contains("Z")]

    referendum_and_areas = pd.merge(
        referendum,
        regions_and_departments,
        left_on="Department code",
        right_on="code_dep",
        how="inner",
    )

    return referendum_and_areas


def compute_referendum_result_by_regions(referendum_and_areas):
    """Return a table with the absolute count for each region.

    (garde ta docstring d'origine)
    """
    counts = ["Registered", "Abstentions", "Null", "Choice A", "Choice B"]

    referendum_result_by_regions = (
        referendum_and_areas.groupby(["code_reg", "name_reg"])[counts]
        .sum()
        .reset_index(level="name_reg")
    )

    return referendum_result_by_regions


def plot_referendum_map(referendum_result_by_regions):
    """Plot a map with the results from the referendum.

    (garde ta docstring d'origine)
    """
    geo = gpd.read_file("data/regions.geojson")

    referendum_map = pd.merge(
        geo,
        referendum_result_by_regions.reset_index(),
        left_on="code",
        right_on="code_reg",
        how="inner",
    )

    expressed = referendum_map["Choice A"] + referendum_map["Choice B"]
    referendum_map["ratio"] = referendum_map["Choice A"] / expressed
    referendum_map.plot(column="ratio", legend=True)

    return referendum_map


if __name__ == "__main__":

    referendum, df_reg, df_dep = load_data()
    regions_and_departments = merge_regions_and_departments(
        df_reg, df_dep
    )
    referendum_and_areas = merge_referendum_and_areas(
        referendum, regions_and_departments
    )
    referendum_results = compute_referendum_result_by_regions(
        referendum_and_areas
    )
    print(referendum_results)

    plot_referendum_map(referendum_results)
    plt.show()
