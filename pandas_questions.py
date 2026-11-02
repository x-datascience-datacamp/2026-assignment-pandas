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
    referendum = pd.DataFrame(pd.read_csv("data/referendum.csv", sep=";"))
    regions = pd.DataFrame(pd.read_csv("data/regions.csv"))
    departments = pd.DataFrame(pd.read_csv("data/departments.csv"))
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
        "code": "code_dep",
        "name": "name_dep"
    })
    merged = pd.merge(regions,departments,left_on="code_reg",right_on="region_code")
    return merged[["code_reg", "name_reg", "code_dep", "name_dep"]]



def merge_referendum_and_areas(referendum, regions_and_departments):
    """Merge referendum and regions_and_departments in one DataFrame.

    You can drop the lines relative to DOM-TOM-COM departments, and the
    french living abroad, which all have a code that contains `Z`.

    DOM-TOM-COM departments are departements that are remote from metropolitan
    France, like Guadaloupe, Reunion, or Tahiti.
    """
    referendum = referendum.copy()
    referendum["Department code"] = (referendum["Department code"].str.zfill(2))
    referendum = referendum[~referendum["Department code"].str.contains("Z")]
    merged = pd.merge(
        referendum,
        regions_and_departments,
        left_on="Department code",
        right_on="code_dep"
    )
    return merged


def compute_referendum_result_by_regions(referendum_and_areas):
    """Return a table with the absolute count for each region.

    The return DataFrame should be indexed by `code_reg` and have columns:
    ['name_reg', 'Registered', 'Abstentions', 'Null', 'Choice A', 'Choice B']
    """
    final=pd.DataFrame({
        "name_reg":[],
        "Registered":[],
        "Abstentions":[],
        "Null":[],
        "Choice A":[],
        "Choice B":[]
    })
    for j in referendum_and_areas["code_reg"].unique():
        final.loc[j] = ["", 0, 0, 0, 0, 0]
        for i in range (len(referendum_and_areas)):
                if referendum_and_areas["code_reg"].iloc[i] == j:
                    final.loc[j, "name_reg"] = referendum_and_areas["name_reg"].iloc[i]
                    final.loc[j, "Registered"] += (
                        referendum_and_areas["Registered"].iloc[i]
                    )
                    final.loc[j, "Abstentions"] += (
                        referendum_and_areas["Abstentions"].iloc[i]
                    )
                    final.loc[j, "Null"] += referendum_and_areas["Null"].iloc[i]
                    final.loc[j, "Choice A"] += referendum_and_areas["Choice A"].iloc[i]
                    final.loc[j, "Choice B"] += referendum_and_areas["Choice B"].iloc[i]
    final.index.name = "code_reg"
    return final


def plot_referendum_map(referendum_result_by_regions):
    """Plot a map with the results from the referendum.

    * Load the geographic data with geopandas from `regions.geojson`.
    * Merge these info into `referendum_result_by_regions`.
    * Use the method `GeoDataFrame.plot` to display the result map. The results
      should display the rate of 'Choice A' over all expressed ballots.
    * Return a gpd.GeoDataFrame with a column 'ratio' containing the results.
    """
    data = gpd.read_file("data/regions.geojson")
    data["code"] = data["code"].astype(referendum_result_by_regions.index.dtype)
    merged = data.merge(
        referendum_result_by_regions,
        left_on="code",
        right_index=True
    )
    merged["ratio"] = merged["Choice A"] / (merged["Choice A"] + merged["Choice B"])
    merged.plot(column="ratio", legend=True)
    return merged


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
