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
from pathlib import Path


DATA_PATH = Path(__file__).parent / "data"


def load_data():
    """Load data from the CSV files referundum/regions/departments."""
    referendum = pd.read_csv(DATA_PATH /"referendum.csv", sep=";")
    regions = pd.read_csv(DATA_PATH / "regions.csv")
    departments = pd.read_csv(DATA_PATH / "departments.csv")
    return referendum, regions, departments


def merge_regions_and_departments(regions, departments):
    """Merge regions and departments in one DataFrame.

    The columns in the final DataFrame should be:
    ['code_reg', 'name_reg', 'code_dep', 'name_dep']
    """
    regions = regions.rename(columns={
        "code": "code_reg",
        "name": "name_reg"
    })
    departments = departments.rename(columns={
        "region_code": "code_reg",
        "code": "code_dep",
        "name": "name_dep"
    })
    df = pd.merge(
        regions,
        departments,
        on="code_reg",
        how="inner"
    )
    return df[["code_reg", "name_reg", "code_dep", "name_dep"]]


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
    df = pd.merge(
        referendum,
        regions_and_departments,
        left_on="Department code",
        right_on="code_dep",
        how="inner"
    )

    df = df[~df["Department code"].astype(str).str.contains("Z", na=False)]
    return df


def compute_referendum_result_by_regions(referendum_and_areas):
    """Return a table with the absolute count for each region.

    The return DataFrame should be indexed by `code_reg` and have columns:
    ['name_reg', 'Registered', 'Abstentions', 'Null', 'Choice A', 'Choice B']
    """
    result = referendum_and_areas.groupby("code_reg").agg({
        "name_reg": "first",
        "Registered": "sum",
        "Abstentions": "sum",
        "Null": "sum",
        "Choice A": "sum",
        "Choice B": "sum"
    })

    return result

def plot_referendum_map(referendum_result_by_regions):
    """Plot a map with the results from the referendum.

    * Load the geographic data with geopandas from `regions.geojson`.
    * Merge these info into `referendum_result_by_regions`.
    * Use the method `GeoDataFrame.plot` to display the result map. The results
      should display the rate of 'Choice A' over all expressed ballots.
    * Return a gpd.GeoDataFrame with a column 'ratio' containing the results.
    """
    regions_geo = gpd.read_file(DATA_PATH / "regions.geojson")
    result = referendum_result_by_regions.reset_index()
    gdf = regions_geo.merge(
        result,
        left_on="code",
        right_on="code_reg",
        how="inner"
    )
    total = gdf["Choice A"] + gdf["Choice B"]
    gdf["ratio"] = gdf["Choice A"] / total.where(total != 0)
    gdf.plot(
        column="ratio",
        legend=True,
        cmap="OrRd",
        figsize=(12, 8)
    )
    plt.title("Referendum results by region - Choice A")
    plt.axis("off")
    return gdf


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
