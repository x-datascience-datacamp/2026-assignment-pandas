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
    referendum = pd.read_csv(
        "data/referendum.csv", sep=";", dtype={"Department code": str}
    )
    # The referendum file writes department codes as "1" instead of "01".
    referendum["Department code"] = referendum["Department code"].str.zfill(2)
    regions = pd.read_csv("data/regions.csv", dtype={"code": str})
    departments = pd.read_csv(
        "data/departments.csv", dtype={"code": str, "region_code": str}
    )

    return referendum, regions, departments


def merge_regions_and_departments(regions, departments):
    """Merge regions and departments in one DataFrame.

    The columns in the final DataFrame should be:
    ['code_reg', 'name_reg', 'code_dep', 'name_dep']
    """
    regions = regions[["code", "name"]].rename(
        columns={"code": "code_reg", "name": "name_reg"}
    )
    departments = departments[["region_code", "code", "name"]].rename(
        columns={
            "region_code": "code_reg",
            "code": "code_dep",
            "name": "name_dep",
        }
    )
    merged = pd.merge(regions, departments, on="code_reg", how="inner")

    return merged[["code_reg", "name_reg", "code_dep", "name_dep"]]


def merge_referendum_and_areas(referendum, regions_and_departments):
    """Merge referendum and regions_and_departments in one DataFrame.

    You can drop the lines relative to DOM-TOM-COM departments, and the
    french living abroad, which all have a code that contains `Z`.

    DOM-TOM-COM departments are departements that are remote from metropolitan
    France, like Guadaloupe, Reunion, or Tahiti.
    """
    referendum = referendum[
        ~referendum["Department code"].str.contains("Z", na=False)
    ]

    return pd.merge(
        referendum,
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
    counts = ["Registered", "Abstentions", "Null", "Choice A", "Choice B"]
    grouped = referendum_and_areas.groupby(["code_reg", "name_reg"])[counts]
    result = grouped.sum().reset_index().set_index("code_reg")

    return result[["name_reg"] + counts]


def plot_referendum_map(referendum_result_by_regions):
    """Plot a map with the results from the referendum.

    * Load the geographic data with geopandas from `regions.geojson`.
    * Merge these info into `referendum_result_by_regions`.
    * Use the method `GeoDataFrame.plot` to display the result map. The results
      should display the rate of 'Choice A' over all expressed ballots.
    * Return a gpd.GeoDataFrame with a column 'ratio' containing the results.
    """
    geo = gpd.read_file("data/regions.geojson")
    geo["code"] = geo["code"].astype(str)

    results = referendum_result_by_regions.reset_index()
    results["code_reg"] = results["code_reg"].astype(str)

    gdf = geo.merge(results, left_on="code", right_on="code_reg", how="inner")
    gdf["ratio"] = gdf["Choice A"] / (gdf["Choice A"] + gdf["Choice B"])

    gdf.plot(column="ratio", legend=True)
    plt.title("Rate of Choice A over expressed ballots")

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
