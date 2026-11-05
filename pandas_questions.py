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
from config import DATA_DIR


def load_data():
    """Load data from the CSV files in the data directory."""
    referendum = pd.read_csv(DATA_DIR / "referendum.csv", sep=";")
    regions = pd.read_csv(DATA_DIR / "regions.csv")
    departments = pd.read_csv(DATA_DIR / "departments.csv")

    return referendum, regions, departments


def merge_regions_and_departments(regions, departments):
    """Merge regions and departments in one DataFrame.

    The columns in the final DataFrame should be:
    ['code_reg', 'name_reg', 'code_dep', 'name_dep']
    """
    region_columns = regions[["code", "name"]].rename(
        columns={"code": "code_reg", "name": "name_reg"}
    )
    department_columns = departments[["region_code", "code", "name"]].rename(
        columns={"region_code": "code_reg", "code": "code_dep", "name": "name_dep"}
    )
    return pd.merge(region_columns, department_columns, on="code_reg")


def merge_referendum_and_areas(referendum, regions_and_departments):
    """Merge referendum and regions_and_departments in one DataFrame.

    You can drop the lines relative to DOM-TOM-COM departments, and the
    french living abroad, which all have a code that contains `Z`.

    DOM-TOM-COM departments are departments that are remote from metropolitan
    France, like Guadaloupe, Reunion, or Tahiti.
    """
    metropolitan_referendum = referendum[
        ~referendum["Department code"].str.contains("Z")
    ]
    metropolitan_referendum = metropolitan_referendum.assign(
        code_dep=metropolitan_referendum["Department code"].str.zfill(2)
    )
    return pd.merge(metropolitan_referendum, regions_and_departments, on="code_dep")


def compute_referendum_result_by_regions(referendum_and_areas):
    """Return a table with the absolute count for each region.

    The return DataFrame should be indexed by `code_reg` and have columns:
    ['name_reg', 'Registered', 'Abstentions', 'Null', 'Choice A', 'Choice B']
    """
    counts = ["Registered", "Abstentions", "Null", "Choice A", "Choice B"]
    return (
        referendum_and_areas.groupby(["code_reg", "name_reg"])[counts]
        .sum()
        .reset_index("name_reg")
    )


def plot_referendum_map(referendum_result_by_regions):
    """Plot a map with the results from the referendum.

    * Load the geographic data with geopandas from `regions.geojson`.
    * Merge these info into `referendum_result_by_regions`.
    * Use the method `GeoDataFrame.plot` to display the result map. The results
      should display the rate of 'Choice A' over all expressed ballots.
    * Return a gpd.GeoDataFrame with a column 'ratio' containing the results.
    """
    regions = gpd.read_file(DATA_DIR / "regions.geojson")

    regions = regions.merge(
        referendum_result_by_regions, left_on="code", right_index=True
    )
    regions["ratio"] = regions["Choice A"] / (regions["Choice A"] + regions["Choice B"])
    regions.plot(
        column="ratio",
        legend=True,
        legend_kwds={"label": "Choice A share", "shrink": 0.7},
        edgecolor="white",
    )

    return regions


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
