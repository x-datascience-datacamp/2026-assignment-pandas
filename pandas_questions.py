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
    regions = regions.rename(columns={"code": "code_reg", "name": "name_reg"})
    departments = departments.rename(columns={"code": "code_dep", "name": "name_dep"})
    regions = regions.drop(columns=["slug", "id"])
    departments = departments.drop(columns=["slug", "id"])

    df_merge = pd.merge(
        regions,
        departments,
        left_on="code_reg",
        right_on="region_code",
        how="inner",
    )
    df_merge = df_merge.drop(columns=["region_code"])
    return df_merge


def merge_referendum_and_areas(referendum, regions_and_departments):
    """Merge referendum and regions_and_departments in one DataFrame.

    You can drop the lines relative to DOM-TOM-COM departments, and the
    french living abroad, which all have a code that contains `Z`.

    DOM-TOM-COM departments are departements that are remote from metropolitan
    France, like Guadaloupe, Reunion, or Tahiti.
    """
    referendum = referendum.loc[~referendum["Department code"].str.contains("Z")]
    # change 1 in Department code to 01, 2 to 02, etc.
    # to match the department code in regions_and_departments
    referendum["Department code"] = referendum["Department code"].apply(
        lambda x: x.zfill(2)
    )
    df_merge_areas = pd.merge(
        referendum,
        regions_and_departments,
        left_on="Department code",
        right_on="code_dep",
        how="inner",
    )

    return df_merge_areas


def compute_referendum_result_by_regions(referendum_and_areas):
    """Return a table with the absolute count for each region.

    The return DataFrame should be indexed by `code_reg` and have columns:
    ['name_reg', 'Registered', 'Abstentions', 'Null', 'Choice A', 'Choice B']
    """
    referendum_result = referendum_and_areas.groupby(["code_reg", "name_reg"]).sum()
    # index by `code_reg`
    referendum_result = referendum_result.reset_index()
    referendum_result = referendum_result.set_index("code_reg")
    referendum_result = referendum_result[
        ["name_reg", "Registered", "Abstentions", "Null", "Choice A", "Choice B"]
    ]

    return referendum_result


def plot_referendum_map(referendum_result_by_regions):
    """Plot a map with the results from the referendum.

    * Load the geographic data with geopandas from `regions.geojson`.
    * Merge these info into `referendum_result_by_regions`.
    * Use the method `GeoDataFrame.plot` to display the result map. The results
      should display the rate of 'Choice A' over all expressed ballots.
    * Return a gpd.GeoDataFrame with a column 'ratio' containing the results.
    """
    geo_df = gpd.read_file("data/regions.geojson")
    df_merge = pd.merge(
        geo_df,
        referendum_result_by_regions,
        left_on="code",
        right_on="code_reg",
        how="inner",
    )
    df_merge["ratio"] = df_merge["Choice A"] / (
        df_merge["Choice A"] + df_merge["Choice B"]
    )
    df_merge.plot(
        column="ratio",
        cmap="coolwarm",
        legend=True,
        legend_kwds={"label": "Choice A Ratio", "orientation": "horizontal"},
    )
    geo_df = gpd.GeoDataFrame(df_merge)

    return geo_df


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
