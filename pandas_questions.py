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
    regions = pd.read_csv("data/regions.csv", sep=",")
    departments = pd.read_csv("data/departments.csv", sep=",")

    return referendum, regions, departments


def merge_regions_and_departments(regions, departments):
    """Merge regions and departments in one DataFrame.

    The columns in the final DataFrame should be:
    ['code_reg', 'name_reg', 'code_dep', 'name_dep']
    """
    departments = departments.rename(columns={"code": "code_dep", "name": "name_dep"})
    merged = regions.merge(departments, left_on="code", right_on="region_code")
    merged = merged.rename(columns={"code": "code_reg", "name": "name_reg"})
    return merged[["code_reg", "name_reg", "code_dep", "name_dep"]]


def merge_referendum_and_areas(referendum, regions_and_departments):
    """Merge referendum and regions_and_departments in one DataFrame.

    You can drop the lines relative to DOM-TOM-COM departments, and the
    french living abroad, which all have a code that contains `Z`.

    DOM-TOM-COM departments are departements that are remote from metropolitan
    France, like Guadaloupe, Reunion, or Tahiti.
    """
    idx = referendum["Department code"].str.contains("Z")
    referendum.drop(referendum[idx].index, inplace=True)
    regions_and_departments['code_dep'] = (regions_and_departments['code_dep']
                                           .astype(str)
                                           .str
                                           .lstrip('0'))
    merged = (regions_and_departments
              .merge(referendum, left_on="code_dep", right_on="Department code"))
    return merged


def compute_referendum_result_by_regions(referendum_and_areas):
    """Return a table with the absolute count for each region.

    The return DataFrame should be indexed by `code_reg` and have columns:
    ['name_reg', 'Registered', 'Abstentions', 'Null', 'Choice A', 'Choice B']
    """
    df = referendum_and_areas.groupby("name_reg", as_index=False).agg({
        "Registered": "sum",
        "Abstentions": "sum",
        "Null": "sum",
        "Choice A": "sum",
        "Choice B": "sum"
    })
    return df


def plot_referendum_map(referendum_result_by_regions):
    """Plot a map with the results from the referendum.

    * Load the geographic data with geopandas from `regions.geojson`.
    * Merge these info into `referendum_result_by_regions`.
    * Use the method `GeoDataFrame.plot` to display the result map. The results
      should display the rate of 'Choice A' over all expressed ballots.
    * Return a gpd.GeoDataFrame with a column 'ratio' containing the results.
    """

    gdf_regions = gpd.read_file("data/regions.geojson")

    gdf_merged = (gdf_regions.
                  merge(referendum_result_by_regions,left_on="nom",right_on="name_reg")
                  )
    gdf_merged["ratio"] = gdf_merged["Choice A"] / (gdf_merged[["Choice A", "Choice B"]]
                                                    .sum(axis=1))

    fig, ax = plt.subplots(1, 1, figsize=(10, 8))
    gdf_merged.plot(
        column="ratio",
        cmap="OrRd",
        legend=True,
        legend_kwds={"label": "Taux de 'Choice A'"},
        ax=ax,
    )
    ax.set_title("Résultats du référendum par région (Proportion de 'Choice A')")
    ax.axis("off")

    return gdf_merged


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
