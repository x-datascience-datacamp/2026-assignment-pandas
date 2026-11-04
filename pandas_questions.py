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
    """Load data from the CSV files in data/."""
    regions = pd.read_csv("data/regions.csv")
    departments = pd.read_csv("data/departments.csv")
    referendum = pd.read_csv("data/referendum.csv", sep=";")

    return referendum, regions, departments


def merge_regions_and_departments(regions, departments):
    """Merge regions and departments in one DataFrame.

    The columns in the final DataFrame should be:
    ['code_reg', 'name_reg', 'code_dep', 'name_dep']
    """
    dept_renamed = departments.rename(
        columns={"code": "code_dep", "name": "name_dep"}
    )
    reg_renamed = regions.rename(
        columns={"code": "code_reg", "name": "name_reg"}
    )

    dept_renamed["code_dep"] = dept_renamed["code_dep"].astype(str).str.zfill(2)
    reg_renamed["code_reg"] = reg_renamed["code_reg"].astype(str)
    dept_renamed["region_code"] = dept_renamed["region_code"].astype(str)

    merged = pd.merge(
        dept_renamed,
        reg_renamed,
        left_on="region_code",
        right_on="code_reg",
        how="inner",
    )
    return merged[["code_reg", "name_reg", "code_dep", "name_dep"]]


def merge_referendum_and_areas(referendum, regions_and_departments):
    """Merge referendum and regions_and_departments in one DataFrame.

    You can drop the lines relative to DOM-TOM-COM departments, and the
    french living abroad, which all have a code that contains `Z`.
    """
    clean_ref = referendum[
        ~referendum["Department code"]
        .astype(str)
        .str.contains("Z", na=False)
    ].copy()

    clean_ref["Department code"] = (
        clean_ref["Department code"].astype(str).str.zfill(2)
    )
    regions_and_departments = regions_and_departments.copy()
    regions_and_departments["code_dep"] = (
        regions_and_departments["code_dep"].astype(str).str.zfill(2)
    )

    return pd.merge(
        clean_ref,
        regions_and_departments,
        left_on="Department code",
        right_on="code_dep",
        how="inner",
    )


def compute_referendum_result_by_regions(referendum_and_areas):
    """Return a table with the absolute count for each region.

    The return DataFrame should be indexed by `code_reg` and have columns:
    ['name_reg', 'Registered', 'Abstentions', 'Null', 'Choice A', 'Choice B']
    """
    cols = ["Registered", "Abstentions", "Null", "Choice A", "Choice B"]
    agg_df = (
        referendum_and_areas
        .groupby(["code_reg", "name_reg"])[cols]
        .sum()
        .reset_index()
        .set_index("code_reg")
    )
    return agg_df[["name_reg"] + cols]


def plot_referendum_map(referendum_result_by_regions):
    """Plot a map with the results from the referendum.

    * Load the geographic data with geopandas from `data/regions.geojson`.
    * Merge these info into `referendum_result_by_regions`.
    * Use the method `GeoDataFrame.plot` to display the result map.
    * Return a gpd.GeoDataFrame with a column 'ratio' containing results.
    """
    geo_df = gpd.read_file("data/regions.geojson")
    geo_df["code"] = geo_df["code"].astype(str)

    res_df = referendum_result_by_regions.reset_index()
    res_df["code_reg"] = res_df["code_reg"].astype(str)

    merged_geo = geo_df.merge(
        res_df,
        left_on="code",
        right_on="code_reg",
        how="inner",
    )

    choice_a = merged_geo["Choice A"]
    choice_b = merged_geo["Choice B"]
    merged_geo["ratio"] = choice_a / (choice_a + choice_b)

    merged_geo.plot(
        column="ratio",
        cmap="coolwarm",
        legend=True,
        edgecolor="black",
    )
    return merged_geo


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
