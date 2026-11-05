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
    """Load data from the CSV files referendum/regions/departments."""
    referendum = pd.read_csv(
        "data/referendum.csv",
        sep=";",
        dtype={"Department code": str}
    )
    departments = pd.read_csv("data/departments.csv", dtype=str)
    regions = pd.read_csv("data/regions.csv", dtype=str)

    return referendum, regions, departments


def merge_regions_and_departments(regions, departments):
    """Merge regions and departments in one DataFrame."""
    regions_and_departments = pd.merge(
        regions,
        departments,
        left_on="code",
        right_on="region_code",
        how="inner"
    )

    regions_and_departments = regions_and_departments.rename(
        columns={
            "code_x": "code_reg",
            "code_y": "code_dep",
            "name_x": "name_reg",
            "name_y": "name_dep"
        }
    )

    return regions_and_departments[
        ["code_reg", "name_reg", "code_dep", "name_dep"]
    ]


def merge_referendum_and_areas(referendum, regions_and_departments):
    """Merge referendum and geographical areas."""
    referendum1 = referendum.copy()

    referendum1 = referendum1[
        ~referendum1["Department code"].str.contains("Z", na=False)
    ].copy()

    referendum1["Department code"] = (
        referendum1["Department code"].str.zfill(2)
    )

    referendum_and_areas = pd.merge(
        referendum1,
        regions_and_departments,
        left_on="Department code",
        right_on="code_dep",
        how="inner"
    )

    return referendum_and_areas


def compute_referendum_result_by_regions(referendum_and_areas):
    """Return a table with the absolute count for each region.

    The return DataFrame should be indexed by `code_reg` and have columns:
    ['name_reg', 'Registered', 'Abstentions', 'Null', 'Choice A', 'Choice B']
    """
    result = referendum_and_areas.groupby(["name_reg", "code_reg"])[
        ['Registered', 'Abstentions', 'Null', 'Choice A', 'Choice B']].sum()
    result = result.reset_index().set_index("code_reg")
    return result


def plot_referendum_map(referendum_result_by_regions):
    """Plot a map with the results from the referendum.

    * Load the geographic data with geopandas from `regions.geojson`.
    * Merge these info into `referendum_result_by_regions`.
    * Use the method `GeoDataFrame.plot` to display the result map. The results
      should display the rate of 'Choice A' over all expressed ballots.
    * Return a gpd.GeoDataFrame with a column 'ratio' containing the results.
    """
    geo_data = gpd.read_file("data/regions.geojson")
    geo_data["code"] = geo_data["code"].astype(str).str.zfill(2)
    results = referendum_result_by_regions.copy()
    results.index = results.index.astype(str).str.zfill(2)

    gdf = geo_data.merge(results, left_on="code", right_index=True, how="inner")
    gdf["ratio"] = gdf["Choice A"] / (gdf["Choice A"] + gdf["Choice B"])
    gdf.plot(column="ratio", legend=True)

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
