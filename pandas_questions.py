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
    referendum = pd.DataFrame(pd.read_csv("data/referendum.csv",  sep=";"))
    regions = pd.DataFrame(pd.read_csv("data/regions.csv"))
    departments = pd.DataFrame(pd.read_csv("data/departments.csv"))

    return referendum, regions, departments


def merge_regions_and_departments(regions, departments):
    """Merge regions and departments in one DataFrame.

    The columns in the final DataFrame should be:
    ['code_reg', 'name_reg', 'code_dep', 'name_dep']
    """
    regions_clean=regions.rename(columns={"code": "code_reg", "name": "name_reg"})
    departments_clean=departments.rename(columns={"name": "name_dep",
                                                  "code": "code_dep"})
    regions_and_departments=regions_clean.merge(departments_clean,
                                                left_on="code_reg",
                                                right_on="region_code",)

    return pd.DataFrame(regions_and_departments[["code_reg",
                                                 "name_reg",
                                                 "code_dep",
                                                 "name_dep"]])


def merge_referendum_and_areas(referendum, regions_and_departments):
    """Merge referendum and regions_and_departments in one DataFrame.

    You can drop the lines relative to DOM-TOM-COM departments, and the
    french living abroad, which all have a code that contains `Z`.

    DOM-TOM-COM departments are departements that are remote from metropolitan
    France, like Guadaloupe, Reunion, or Tahiti.
    """
    referendum = referendum.copy()
    referendum["Department code"] = (
        referendum["Department code"].str.zfill(2)
    )
    referendum_and_areas=regions_and_departments.merge(referendum,
                                                       left_on="code_dep",
                                                       right_on="Department code")
    is_overseas=referendum_and_areas["Department code"].str.startswith("Z")
    referendum_and_areas=referendum_and_areas[~is_overseas]
    return pd.DataFrame(referendum_and_areas)


def compute_referendum_result_by_regions(referendum_and_areas):
    """Return a table with the absolute count for each region.

    The return DataFrame should be indexed by `code_reg` and have columns:
    ['name_reg', 'Registered', 'Abstentions', 'Null', 'Choice A', 'Choice B']
    """
    referendum_by_reg=referendum_and_areas[["code_reg",
                                              "name_reg",
                                              "Registered",
                                              "Abstentions",
                                              "Null",
                                              "Choice A",
                                              "Choice B"]]
    referendum_by_reg=referendum_by_reg.groupby(["code_reg",
                                                 "name_reg"])
    referendum_by_reg=referendum_by_reg[["Registered",
                                         "Abstentions",
                                         "Null",
                                         "Choice A",
                                         "Choice B"]].sum()
    referendum_by_reg=referendum_by_reg.reset_index(level="name_reg")
    return pd.DataFrame(referendum_by_reg)


def plot_referendum_map(referendum_result_by_regions):
    """Plot a map with the results from the referendum.

    * Load the geographic data with geopandas from `regions.geojson`.
    * Merge these info into `referendum_result_by_regions`.
    * Use the method `GeoDataFrame.plot` to display the result map. The results
      should display the rate of 'Choice A' over all expressed ballots.
    * Return a gpd.GeoDataFrame with a column 'ratio' containing the results.
    """
    geo_data=gpd.read_file("data/regions.geojson")
    geo_data_ref=geo_data.merge(referendum_result_by_regions,
                                left_on="code",
                                right_index=True)
    total_votes=geo_data_ref["Choice A"]+geo_data_ref["Choice B"]
    geo_data_ref["ratio"]=geo_data_ref["Choice A"]/total_votes
    geo_data_ref.plot(column="ratio", legend=True)
    return gpd.GeoDataFrame(geo_data_ref)


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
    plt.savefig("map.png")
    plt.show()
