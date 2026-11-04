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

    res = pd.merge(departments,regions,left_on="region_code",right_on="code")
    res = res.drop(columns=["id_x", "slug_x", "id_y", "slug_y", "region_code"]
    )
    res = res.rename(
        columns={
            "code_x": "code_dep",
            "name_x": "name_dep",
            "code_y": "code_reg",
            "name_y": "name_reg",
        }
    )
    return res[["code_reg", "name_reg", "code_dep", "name_dep"]]


def merge_referendum_and_areas(referendum, regions_and_departments):
    """Merge referendum and regions_and_departments in one DataFrame.

    You can drop the lines relative to DOM-TOM-COM departments, and the
    french living abroad, which all have a code that contains `Z`.

    DOM-TOM-COM departments are departements that are remote from metropolitan
    France, like Guadaloupe, Reunion, or Tahiti.
    """

    areas = regions_and_departments.copy()
    areas["code_dep"] = areas["code_dep"].str.replace(
        r"^0", "", regex=True
    )
    referendum = referendum[~referendum["Department code"].str.contains("Z", na=False)
    ]

    return pd.merge(
        referendum,
        areas,
        left_on="Department code",
        right_on="code_dep",
    )


def compute_referendum_result_by_regions(referendum_and_areas):
    """Return a table with the absolute count for each region.

    The return DataFrame should be indexed by `code_reg` and have columns:
    ['name_reg', 'Registered', 'Abstentions', 'Null', 'Choice A', 'Choice B']
    """

    return referendum_and_areas.groupby("code_reg").agg(
        name_reg=("name_reg", "first"),
        Registered=("Registered", "sum"),
        Abstentions=("Abstentions", "sum"),
        Null=("Null", "sum"),
        **{
            "Choice A": ("Choice A", "sum"),
            "Choice B": ("Choice B", "sum"),
        },
    )


def plot_referendum_map(referendum_result_by_regions):
    """Plot a map with the results from the referendum.

    * Load the geographic data with geopandas from `regions.geojson`.
    * Merge these info into `referendum_result_by_regions`.
    * Use the method `GeoDataFrame.plot` to display the result map. The results
      should display the rate of 'Choice A' over all expressed ballots.
    * Return a gpd.GeoDataFrame with a column 'ratio' containing the results.
    """

    regions = gpd.read_file("data/regions.geojson").rename(
        columns={"code": "code_reg", "nom": "name_reg"}
    )
    results = referendum_result_by_regions.copy()
    results.index = results.index.astype(str)
    results = results.drop(columns="name_reg")

    referendum_map = regions.merge(
        results, left_on="code_reg", right_index=True, how="left"
    )
    referendum_map["ratio"] = referendum_map["Choice A"] / (
        referendum_map["Choice A"] + referendum_map["Choice B"]
    )
    referendum_map.plot(column="ratio", legend=True)

    return referendum_map


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
