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
    """Load the referendum, regions, and departments CSV files.

    Return three pandas DataFrames:
    referendum, regions, and departments.
    """
    referendum = pd.read_csv(
        "data/referendum.csv",
        sep=";",
        dtype={"Department code": str}
    )

    regions = pd.read_csv(
        "data/regions.csv",
        dtype={"code": str}
    )

    departments = pd.read_csv(
        "data/departments.csv",
        dtype={"code": str, "region_code": str}
    )

    return referendum, regions, departments


def merge_regions_and_departments(regions, departments):
    """Merge referendum and regions_and_departments in one DataFrame.

    You can drop the lines relative to DOM-TOM-COM departments, and the
    french living abroad, which all have a code that contains `Z`.

    DOM-TOM-COM departments are departements that are remote from metropolitan
    France, like Guadaloupe, Reunion, or Tahiti.
    """
    df = pd.merge(
        regions,
        departments,
        left_on="code",
        right_on="region_code"
    )

    df = df.rename(columns={
        "code_x": "code_reg",
        "code_y": "code_dep",
        "name_x": "name_reg",
        "name_y": "name_dep"
    })

    return df[["code_reg", "name_reg", "code_dep", "name_dep"]]


def merge_referendum_and_areas(referendum, regions_and_departments):
    """Return a table with the absolute count for each region.

    The return DataFrame should be indexed by `code_reg` and have columns:
    ['name_reg', 'Registered', 'Abstentions', 'Null', 'Choice A', 'Choice B']
    """
    referendum = referendum.copy()
    regions_and_departments = regions_and_departments.copy()

    referendum["Department code"] = (
        referendum["Department code"].str.strip().str.zfill(2)
    )

    regions_and_departments["code_dep"] = (
        regions_and_departments["code_dep"].str.strip().str.zfill(2)
    )

    df = pd.merge(
        referendum,
        regions_and_departments,
        left_on="Department code",
        right_on="code_dep",
        how="inner"
    )

    df = df.dropna()

    return df


def compute_referendum_result_by_regions(referendum_and_areas):
    """Plot a map with the results from the referendum.

    * Load the geographic data with geopandas from `regions.geojson`.
    * Merge these info into `referendum_result_by_regions`.
    * Use the method `GeoDataFrame.plot` to display the result map. The results
      should display the rate of 'Choice A' over all expressed ballots.
    * Return a gpd.GeoDataFrame with a column 'ratio' containing the results.
    """
    df = referendum_and_areas.groupby("code_reg").agg({
        "name_reg": "first",
        "Registered": "sum",
        "Abstentions": "sum",
        "Null": "sum",
        "Choice A": "sum",
        "Choice B": "sum"
    })

    return df


def plot_referendum_map(referendum_result_by_regions):
    regions = gpd.read_file("data/regions.geojson")

    regions = regions.merge(
        referendum_result_by_regions,
        left_on="code",
        right_index=True,
        how="left"
    )

    regions["ratio"] = (
        regions["Choice A"] /
        (regions["Choice A"] + regions["Choice B"])
    )

    regions.plot(
        column="ratio",
        legend=True,
        cmap="RdYlBu",
        figsize=(10, 8)
    )

    plt.title("Referendum Results — Choice A")
    plt.axis("off")

    return regions


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
