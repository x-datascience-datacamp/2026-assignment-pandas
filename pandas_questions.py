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
    # Codes such as "01" or "2A" are identifiers, not numbers: read them as
    # strings so that leading zeros are kept and merges work as expected.
    referendum = pd.read_csv(
        "data/referendum.csv", sep=";", dtype={"Department code": str}
    )
    regions = pd.read_csv("data/regions.csv", dtype={"code": str})
    departments = pd.read_csv(
        "data/departments.csv", dtype={"region_code": str, "code": str}
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
            "region_code": "code_reg", "code": "code_dep", "name": "name_dep"
        }
    )

    return pd.merge(regions, departments, on="code_reg", how="inner")


def merge_referendum_and_areas(referendum, regions_and_departments):
    """Merge referendum and regions_and_departments in one DataFrame.

    You can drop the lines relative to DOM-TOM-COM departments, and the
    french living abroad, which all have a code that contains `Z`.

    DOM-TOM-COM departments are departements that are remote from metropolitan
    France, like Guadaloupe, Reunion, or Tahiti.
    """
    referendum = referendum.copy()

    # Drop DOM-TOM-COM and French living abroad (codes containing "Z").
    is_abroad = referendum["Department code"].str.contains("Z")
    referendum = referendum[~is_abroad]

    # The referendum uses "1", "2", ... while departments use "01", "02", ...
    # Pad with a leading zero so that both tables use the same format.
    referendum["code_dep"] = referendum["Department code"].str.zfill(2)

    referendum_and_areas = pd.merge(
        referendum, regions_and_departments, on="code_dep", how="inner"
    )

    return referendum_and_areas.dropna()


def compute_referendum_result_by_regions(referendum_and_areas):
    """Return a table with the absolute count for each region.

    The return DataFrame should be indexed by `code_reg` and have columns:
    ['name_reg', 'Registered', 'Abstentions', 'Null', 'Choice A', 'Choice B']
    """
    count_columns = [
        "Registered", "Abstentions", "Null", "Choice A", "Choice B"
    ]

    # Grouping on both code and name keeps the region name in the result.
    result = (
        referendum_and_areas
        .groupby(["code_reg", "name_reg"])[count_columns]
        .sum()
        .reset_index(level="name_reg")
    )

    return result


def plot_referendum_map(referendum_result_by_regions):
    """Plot a map with the results from the referendum.

    * Load the geographic data with geopandas from `regions.geojson`.
    * Merge these info into `referendum_result_by_regions`.
    * Use the method `GeoDataFrame.plot` to display the result map. The results
      should display the rate of 'Choice A' over all expressed ballots.
    * Return a gpd.GeoDataFrame with a column 'ratio' containing the results.
    """
    regions_geo = gpd.read_file("data/regions.geojson")

    # Merging on the GeoDataFrame (left) keeps the result a GeoDataFrame.
    gdf = regions_geo.merge(
        referendum_result_by_regions,
        left_on="code",
        right_index=True,
        how="inner",
    )

    # Ratio of "Choice A" over the expressed ballots (A + B).
    expressed = gdf["Choice A"] + gdf["Choice B"]
    gdf["ratio"] = gdf["Choice A"] / expressed

    gdf.plot(column="ratio", legend=True, cmap="RdBu")
    plt.title("Referendum: share of 'Choice A' by region")
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
