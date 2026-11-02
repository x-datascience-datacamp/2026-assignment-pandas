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

    df_merged = pd.merge(regions, departments,
                         left_on="code", right_on="region_code",
                         suffixes=("_reg", "_dep"))
    return df_merged[['code_reg', 'name_reg', 'code_dep', 'name_dep']]


def merge_referendum_and_areas(referendum, regions_and_departments):
    """Merge referendum and regions_and_departments in one DataFrame.

    You can drop the lines relative to DOM-TOM-COM departments, and the
    french living abroad, which all have a code that contains `Z`.

    DOM-TOM-COM departments are departements that are remote from metropolitan
    France, like Guadaloupe, Reunion, or Tahiti.
    """
    ref = referendum.copy()
    rd = regions_and_departments.copy()

    ref["Department code"] = ref["Department code"].astype(str).str.zfill(2)
    rd["code_dep"] = rd["code_dep"].astype(str).str.zfill(2)

    df_merged = pd.merge(ref, rd,
                         left_on="Department code", right_on="code_dep")

    df_final = df_merged[~df_merged["Department code"].str.contains("Z")]
    return df_final.dropna()


def compute_referendum_result_by_regions(referendum_and_areas):
    """Return a table with the absolute count for each region.

    The return DataFrame should be indexed by `code_reg` and have columns:
    ['name_reg', 'Registered', 'Abstentions', 'Null', 'Choice A', 'Choice B']
    """
    to_sum = ['Registered', 'Abstentions', 'Null', 'Choice A', 'Choice B']
    df_grouped = referendum_and_areas.groupby(['code_reg', 'name_reg'])[to_sum].sum()
    return df_grouped.reset_index(level='name_reg')


def plot_referendum_map(ref_result_by_reg):
    """Plot a map with the results from the referendum."""


    geo_regions = gpd.read_file("data/regions.geojson")

    total_exprimes = ref_result_by_reg['Choice A'] + ref_result_by_reg['Choice B']
    ref_result_by_reg['ratio'] = ref_result_by_reg['Choice A'] / total_exprimes

    gdf = geo_regions.merge(
        ref_result_by_reg,
        left_on="code",
        right_index=True
    )


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
