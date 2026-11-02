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
    regions = pd.read_csv("data/regions.csv", sep=",")
    departments = pd.read_csv("data/departments.csv", sep=",")

    return referendum, regions, departments


def merge_regions_and_departments(regions, departments):
    """Merge regions and departments in one DataFrame.

    The columns in the final DataFrame should be:
    ['code_reg', 'name_reg', 'code_dep', 'name_dep']
    """

    merged = regions.merge(
        departments, left_on="code", right_on="region_code", how="left"
    )
    merged = merged.rename(
        columns={
            "code_x": "code_reg",
            "name_x": "name_reg",
            "code_y": "code_dep",
            "name_y": "name_dep",
        }
    )
    merged = merged[["code_reg", "name_reg", "code_dep", "name_dep"]]
    print(merged.head())
    return merged


def merge_referendum_and_areas(referendum, regions_and_departments):
    """Merge referendum and regions_and_departments in one DataFrame.

    You can drop the lines relative to DOM-TOM-COM departments, and the
    french living abroad, which all have a code that contains `Z`.

    DOM-TOM-COM departments are departements that are remote from metropolitan
    France, like Guadaloupe, Reunion, or Tahiti.
    """
    referendum["Department code"] = (
        referendum["Department code"].astype(str).str.zfill(2)
    )
    referendum_and_areas = referendum.merge(
        regions_and_departments,
        left_on="Department code",
        right_on="code_dep",
        how="left",
    )
    referendum_and_areas = referendum_and_areas[
        ~referendum_and_areas["Department code"].str.contains("Z")
    ]
    return referendum_and_areas


def compute_referendum_result_by_regions(referendum_and_areas):
    """Return a table with the absolute count for each region.

    The return DataFrame should be indexed by `code_reg` and have columns:
    ['name_reg', 'Registered', 'Abstentions', 'Null', 'Choice A', 'Choice B']
    """
    referendum_result_by_regions = referendum_and_areas.groupby("code_reg").sum()
    referendum_result_by_regions = referendum_result_by_regions[
        ["Registered", "Abstentions", "Null", "Choice A", "Choice B"]
    ]
    referendum_result_by_regions = referendum_result_by_regions.merge(
        referendum_and_areas[["code_reg", "name_reg"]].drop_duplicates(),
        left_index=True,
        right_on="code_reg",
    )
    referendum_result_by_regions = referendum_result_by_regions.set_index("code_reg")
    return referendum_result_by_regions[
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
    regions_geo = gpd.read_file("data/regions.geojson")
    referendum_result_by_regions = regions_geo.merge(
        referendum_result_by_regions, left_on="code", right_on="code_reg"
    )
    referendum_result_by_regions["ratio"] = referendum_result_by_regions["Choice A"] / (
        referendum_result_by_regions["Choice A"]
        + referendum_result_by_regions["Choice B"]
    )
    referendum_result_by_regions.plot(column="ratio", cmap="coolwarm", legend=True)
    return referendum_result_by_regions


if __name__ == "__main__":

    referendum, df_reg, df_dep = load_data()
    regions_and_departments = merge_regions_and_departments(df_reg, df_dep)
    referendum_and_areas = merge_referendum_and_areas(
        referendum, regions_and_departments
    )
    referendum_results = compute_referendum_result_by_regions(referendum_and_areas)
    print(referendum_results)

    plot_referendum_map(referendum_results)
    plt.show()
