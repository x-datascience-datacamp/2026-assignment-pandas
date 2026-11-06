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
    departments = pd.read_csv("data/departments.csv")
    referrendum = pd.read_csv("data/referendum.csv", sep=";")
    regions = pd.read_csv("data/regions.csv")
    return referrendum, regions, departments

def merge_regions_and_departments(regions, departments):
    """Merge regions and departments in one DataFrame.

    The columns in the final DataFrame should be:
    ['code_reg', 'name_reg', 'code_dep', 'name_dep']
    """
    regions = regions.rename(columns={"name":"name_reg", "code":"code_reg"})
    departments = departments.rename(
        columns={"region_code":"code_reg", "name":"name_dep", "code":"code_dep"}
        )

    cc = pd.merge(regions[["name_reg", "code_reg"]],
                  departments[["code_reg", "name_dep", "code_dep"]],
                  on="code_reg", how="left")
    return cc[["code_reg", "name_reg", "code_dep", "name_dep"]]

def merge_referendum_and_areas(referendum, regions_and_departments):
    """Merge referendum and regions_and_departments in one DataFrame.

    You can drop the lines relative to DOM-TOM-COM departments, and the
    french living abroad, which all have a code that contains `Z`.

    DOM-TOM-COM departments are departements that are remote from metropolitan
    France, like Guadaloupe, Reunion, or Tahiti.
    """
    referendum = referendum.copy()

    referendum = referendum[~referendum["Department code"].str.contains("Z")]

    referendum["Department code"] = referendum["Department code"].str.zfill(2)

    return pd.merge(
        referendum,
        regions_and_departments,
        left_on="Department code",
        right_on="code_dep",
    )

def compute_referendum_result_by_regions(referendum_and_areas):
    """Return a table with the absolute count for each region.

    The return DataFrame should be indexed by `code_reg` and have columns:
    ['name_reg', 'Registered', 'Abstentions', 'Null', 'Choice A', 'Choice B']
    """
    counts = ["Registered", "Abstentions", "Null", "Choice A", "Choice B"]

    result = (
        referendum_and_areas
        .groupby(["code_reg", "name_reg"])[counts]
        .sum()
        .reset_index(level="name_reg")
    )
    return result

def plot_referendum_map(referendum_result_by_regions):
    """..."""
    geo_regions = gpd.read_file("data/regions.geojson")

    result = geo_regions.merge(
        referendum_result_by_regions,
        left_on="code",
        right_index=True,
    )

    result["ratio"] = result["Choice A"] / (result["Choice A"] + result["Choice B"])

    result.plot(column="ratio", legend=True, cmap="RdBu")
    return result

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
