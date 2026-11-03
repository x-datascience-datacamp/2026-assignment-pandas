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
    referendum = pd.read_csv("./data/referendum.csv", sep=";", dtype=str)
    regions = pd.read_csv("./data/regions.csv", sep=",", dtype=str)
    departments = pd.read_csv("./data/departments.csv", sep=",", dtype=str)

    # Numeric columns must stay numeric for the sums later
    num_cols = ["Registered", "Abstentions", "Null", "Choice A", "Choice B"]
    referendum[num_cols] = referendum[num_cols].astype(int)

    return referendum, regions, departments


def merge_regions_and_departments(regions, departments):
    """Merge regions and departments in one DataFrame.

    The columns in the final DataFrame should be:
    ['code_reg', 'name_reg', 'code_dep', 'name_dep']
    """


    final_df = pd.DataFrame({})
    final_df = pd.merge(
        regions,
        departments,
        how="inner",
        left_on="code",
        right_on="region_code",suffixes=("_reg", "_dep")
    )
    final_df = final_df[["code_reg", "name_reg", "code_dep", "name_dep"]]


    return final_df


def merge_referendum_and_areas(referendum, regions_and_departments):
    """Merge referendum and regions_and_departments in one DataFrame.

    You can drop the lines relative to DOM-TOM-COM departments, and the
    french living abroad, which all have a code that contains `Z`.

    DOM-TOM-COM departments are departements that are remote from metropolitan
    France, like Guadaloupe, Reunion, or Tahiti.
    """
    referendum = referendum.copy()
    referendum["Department code"] = (
        referendum["Department code"].str.strip().str.zfill(2)
    )

    referendum_and_areas = pd.merge(
        regions_and_departments,
        referendum,
        how="inner",
        left_on="code_dep",
        right_on="Department code",
    )
    return referendum_and_areas


def compute_referendum_result_by_regions(referendum_and_areas):
    """Return a table with the absolute count for each region.

    The return DataFrame should be indexed by `code_reg` and have columns:
    ['name_reg', 'Registered', 'Abstentions', 'Null', 'Choice A', 'Choice B']
    """
    referendum_result_by_regions = referendum_and_areas.groupby(
        "code_reg"
    ).agg({
        "name_reg": "first",
        "Registered": "sum",
        "Abstentions": "sum",
        "Null": "sum",
        "Choice A": "sum",
        "Choice B": "sum",
    })
    return referendum_result_by_regions


def plot_referendum_map(referendum_result_by_regions):
    """Plot a map with the results from the referendum.

    * Load the geographic data with geopandas from `regions.geojson`.
    * Merge these info into `referendum_result_by_regions`.
    * Use the method `GeoDataFrame.plot` to display the result map. The results
      should display the rate of 'Choice A' over all expressed ballots.
    * Return a gpd.GeoDataFrame with a column 'ratio' containing the results.
    """
    geo_data = gpd.read_file("./data/regions.geojson")

    # Reset index to make code_reg available as a column
    results = referendum_result_by_regions.reset_index()

    # Ensure both region codes have the same type
    geo_data["code"] = geo_data["code"].astype(str).str.zfill(2)
    results["code_reg"] = results["code_reg"].astype(str).str.zfill(2)

    # Merge geographic data with referendum results
    region_result = geo_data.merge(
        results,
        how="inner",
        left_on="code",
        right_on="code_reg"
    )

    # Calculate Choice A percentage among expressed ballots
    total_expressed = (
        region_result["Choice A"] + region_result["Choice B"]
    )

    region_result["ratio"] = (
        region_result["Choice A"] / total_expressed
    )

    # Plot the map
    fig, ax = plt.subplots(figsize=(12, 10))

    region_result.plot(
        column="ratio",
        cmap="RdYlBu_r",
        legend=True,
        edgecolor="black",
        linewidth=0.5,
        ax=ax,
        missing_kwds={"color": "lightgrey"}
    )

    ax.set_title(
        "Referendum results by region\nChoice A (% of expressed ballots)",
        fontsize=15
    )

    ax.axis("off")
    plt.tight_layout()

    return region_result



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

