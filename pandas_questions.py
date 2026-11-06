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
    referendum = pd.read_csv("data/referendum.csv",
                              sep=";",
                              dtype={"Department code": str},
                              )
    regions = pd.read_csv("data/regions.csv")
    departments = pd.read_csv("data/departments.csv")
    referendum["Department code"] = referendum["Department code"].str.zfill(2)

    return referendum, regions, departments


def merge_regions_and_departments(regions, departments):
    """Merge regions and departments in one DataFrame.

    The columns in the final DataFrame should be:
    ['code_reg', 'name_reg', 'code_dep', 'name_dep']
    """
    merged = pd.merge(
        departments[["code", "name", "region_code"]].rename(columns={
            "code": "code_dep",
            "name": "name_dep",
            "region_code": "code_reg"
        }),
        regions[["code", "name"]].rename(columns={
            "code": "code_reg",
            "name": "name_reg"
        }),
        on="code_reg",
        how="left",
    )
    return merged


def merge_referendum_and_areas(referendum, regions_and_departments):
    """Merge referendum and regions_and_departments in one DataFrame.

    You can drop the lines relative to DOM-TOM-COM departments, and the
    french living abroad, which all have a code that contains `Z`.

    DOM-TOM-COM departments are departements that are remote from metropolitan
    France, like Guadaloupe, Reunion, or Tahiti.
    """
    referendum = referendum.copy()
    referendum["code_dep"] = referendum["Department code"]
    ref_areas = pd.merge(
        referendum,
        regions_and_departments,
        on="code_dep",
        how="left",
    )

    ref_areas = ref_areas[
        ~ref_areas["code_dep"].str.contains("Z")
    ]
    ref_areas = ref_areas.dropna()
    return ref_areas

def compute_referendum_result_by_regions(referendum_and_areas):
    """Return a table with the absolute count for each region.

    The return DataFrame should be indexed by `code_reg` and have columns:
    ['name_reg', 'Registered', 'Abstentions', 'Null', 'Choice A', 'Choice B']
    """
    results = (
        referendum_and_areas.groupby(["code_reg", "name_reg"])
        .agg(
            Registered=("Registered", "sum"),
            Abstentions=("Abstentions", "sum"),
            Null=("Null", "sum"),
            Choice_A=("Choice A", "sum"),
            Choice_B=("Choice B", "sum")
        )
        .reset_index()
        .set_index("code_reg")
        .sort_index()
    )
    results = results.rename(columns={
        "Choice_A": "Choice A",
        "Choice_B": "Choice B",
    })
    return results


def plot_referendum_map(referendum_result_by_regions):
    """Plot a map with the results from the referendum.

    * Load the geographic data with geopandas from `regions.geojson`.
    * Merge these info into `referendum_result_by_regions`.
    * Use the method `GeoDataFrame.plot` to display the result map. The results
      should display the rate of 'Choice A' over all expressed ballots.
    * Return a gpd.GeoDataFrame with a column 'ratio' containing the results.
    """

    geo_data = gpd.read_file("data/regions.geojson")
    geo_results = geo_data.merge(
        referendum_result_by_regions,
        left_on="code",
        right_on="code_reg",
        how="left",
    )
    expressed_votes = geo_results["Choice A"] + geo_results["Choice B"]
    geo_results["ratio"] = (
        geo_results["Choice A"] / expressed_votes.where(expressed_votes != 0)
    )
    geo_results.plot(
        column="ratio",
        cmap="Blues",
        legend=True,
        edgecolor="black",
        figsize=(12, 10),
    )
    plt.title("Choice A for expressed ballots")
    plt.axis("off")
    plt.show()
    return geo_results


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

    referendum_map = plot_referendum_map(referendum_results)

