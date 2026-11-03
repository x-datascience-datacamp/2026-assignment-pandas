"""Plotting referendum results in pandas.

In short, we want to make beautiful map to report results of a referendum. In
some way, we would like to depict results with something similar to the maps
that you can find here:
https://github.com/x-datascience-datacamp/datacamp-assignment-pandas/blob/main/example_map.png

To do that, you will load the data as pandas.DataFrame, merge the info and
aggregate them by regions and finally plot them on a map using `geopandas`.
"""

import geopandas as gpd
import matplotlib.pyplot as plt
import pandas as pd


def load_data():
    """Load data from the CSV files referendum/regions/departments."""
    referendum = pd.read_csv("data/referendum.csv", sep=";")
    regions = pd.read_csv("data/regions.csv")
    departments = pd.read_csv("data/departments.csv")

    return referendum, regions, departments


def merge_regions_and_departments(regions, departments):
    """Merge regions and departments in one DataFrame.

    The columns in the final DataFrame should be:
    ['code_reg', 'name_reg', 'code_dep', 'name_dep']
    """
    merged = pd.merge(
        regions,
        departments,
        left_on="code",
        right_on="region_code",
        suffixes=("_reg", "_dep"),
    )
    merged = merged.rename(
        columns={
            "code_reg": "code_reg",
            "name_reg": "name_reg",
            "code_dep": "code_dep",
            "name_dep": "name_dep",
        }
    )
    return merged[["code_reg", "name_reg", "code_dep", "name_dep"]]


def merge_referendum_and_areas(referendum, regions_and_departments):
    """Merge referendum and regions_and_departments in one DataFrame.

    You can drop the lines relative to DOM-TOM-COM departments, and the
    french living abroad, which all have a code that contains `Z`.

    DOM-TOM-COM departments are departements that are remote from metropolitan
    France, like Guadaloupe, Reunion, or Tahiti.
    """
    ref = referendum.copy()
    ref = ref[~ref["Department code"].astype(str).str.contains("Z")].copy()
    ref["Department code"] = (
        ref["Department code"].astype(str).str.strip().str.zfill(2)
    )

    areas = regions_and_departments.copy()
    areas["code_dep"] = areas["code_dep"].astype(str).str.strip().str.zfill(2)

    merged = pd.merge(
        ref,
        areas,
        left_on="Department code",
        right_on="code_dep",
        how="inner",
    )
    return merged


def compute_referendum_result_by_regions(referendum_and_areas):
    """Return a table with the absolute count for each region.

    The return DataFrame should be indexed by `code_reg` and have columns:
    ['name_reg', 'Registered', 'Abstentions', 'Null', 'Choice A', 'Choice B']
    """
    res = (
        referendum_and_areas.groupby(["code_reg", "name_reg"])[
            ["Registered", "Abstentions", "Null", "Choice A", "Choice B"]
        ]
        .sum()
        .reset_index()
    )
    res = res.set_index("code_reg")
    return res[
        ["name_reg", "Registered", "Abstentions", "Null", "Choice A", "Choice B"]
    ]


def plot_referendum_map(referendum_result_by_regions):
    """Plot a map with the results from the referendum.

    * Load the geographic data with geopandas from `regions.geojson`.
    * Merge these info into `referendum_result_by_regions`.
    * Use the method `GeoDataFrame.plot` to display the result map. The results
      should display the rate of 'Choice A' over all expressed ballots.
    * Return a gpd.GeoDataFrame with a column 'ratio' containing the results.
    """
    geo_regions = gpd.read_file("data/regions.geojson")


    res = referendum_result_by_regions.copy()
    res["ratio"] = res["Choice A"] / (res["Choice A"] + res["Choice B"])


    geo_regions["code"] = geo_regions["code"].astype(str)
    res.index = res.index.astype(str)

    geo_merged = geo_regions.merge(res, left_on="code", right_index=True)


    fig, ax = plt.subplots(figsize=(10, 8))
    geo_merged.plot(column="ratio", legend=True, ax=ax)
    ax.set_axis_off()

    return geo_merged


if __name__ == "__main__":
    referendum, df_reg, df_dep = load_data()
    regions_and_departments = merge_regions_and_departments(df_reg, df_dep)
    referendum_and_areas = merge_referendum_and_areas(
        referendum, regions_and_departments
    )
    referendum_results = compute_referendum_result_by_regions(
        referendum_and_areas
    )
    print(referendum_results)

    plot_referendum_map(referendum_results)
    plt.show()
