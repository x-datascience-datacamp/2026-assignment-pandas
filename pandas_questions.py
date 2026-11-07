"""Plotting referendum results in pandas.

In short, we want to make beautiful map to report results of a referendum. In
some way, we would like to depict results with something similar to the maps
that you can find here:
https://github.com/x-datascience-datacamp/datacamp-assignment-pandas/blob/main/example_map.png

To do that, you will load the data as pandas.DataFrame, merge the info and
aggregate them by regions and finally plot them on a map using `geopandas`.
"""
from pathlib import Path

import pandas as pd
import geopandas as gpd
import matplotlib.pyplot as plt


def load_data():
    """Load data from the CSV files referundum/regions/departments."""
    data_dir = Path(__file__).parent / "data"
    referendum = pd.read_csv(
        data_dir / "referendum.csv", sep=";",
        dtype={"Department code": "string"},
    )
    regions = pd.read_csv(data_dir / "regions.csv", dtype={"code": "string"})
    departments = pd.read_csv(
        data_dir / "departments.csv",
        dtype={"code": "string", "region_code": "string"},
    )

    return referendum, regions, departments


def merge_regions_and_departments(regions, departments):
    """Merge regions and departments in one DataFrame.

    The columns in the final DataFrame should be:
    ['code_reg', 'name_reg', 'code_dep', 'name_dep']
    """

    regions = regions.rename(columns={"code": "code_reg", "name": "name_reg"})
    departments = departments.rename(columns={
        "region_code": "code_reg", "code": "code_dep", "name": "name_dep",
    })
    return regions[["code_reg", "name_reg"]].merge(
        departments[["code_reg", "code_dep", "name_dep"]],
        on="code_reg", validate="one_to_many",
    )


def merge_referendum_and_areas(referendum, regions_and_departments):
    """Merge referendum and regions_and_departments in one DataFrame.

    You can drop the lines relative to DOM-TOM-COM departments, and the
    french living abroad, which all have a code that contains `Z`.

    DOM-TOM-COM departments are departements that are remote from metropolitan
    France, like Guadaloupe, Reunion, or Tahiti.
    """

    referendum = referendum.loc[
        ~referendum["Department code"].str.contains("Z", na=False)
    ].copy()
    # Keep Corsican codes (2A/2B) while aligning 1 with department 01.
    referendum["Department code"] = (
        referendum["Department code"].str.zfill(2)
    )
    return referendum.merge(
        regions_and_departments, left_on="Department code", right_on="code_dep",
        validate="many_to_one",
    )


def compute_referendum_result_by_regions(referendum_and_areas):
    """Return a table with the absolute count for each region.

    The return DataFrame should be indexed by `code_reg` and have columns:
    ['name_reg', 'Registered', 'Abstentions', 'Null', 'Choice A', 'Choice B']
    """

    counts = ["Registered", "Abstentions", "Null", "Choice A", "Choice B"]
    return (
        referendum_and_areas.groupby(["code_reg", "name_reg"])[counts]
        .sum().reset_index("name_reg")
    )


def plot_referendum_map(referendum_result_by_regions):
    """Plot a map with the results from the referendum.

    * Load the geographic data with geopandas from `regions.geojson`.
    * Merge these info into `referendum_result_by_regions`.
    * Use the method `GeoDataFrame.plot` to display the result map. The results
      should display the rate of 'Choice A' over all expressed ballots.
    * Return a gpd.GeoDataFrame with a column 'ratio' containing the results.
    """

    geography = gpd.read_file(Path(__file__).parent / "data" / "regions.geojson")
    geography["code"] = geography["code"].astype("string").str.zfill(2)
    results = geography.merge(
        referendum_result_by_regions, left_on="code", right_index=True,
        validate="one_to_one",
    )
    expressed = results["Choice A"] + results["Choice B"]
    results["ratio"] = results["Choice A"] / expressed.where(expressed.ne(0))
    ax = results.plot(
        column="ratio", cmap="RdBu", vmin=0, vmax=1, legend=True,
        edgecolor="white", linewidth=0.5,
        legend_kwds={"label": "Choice A / expressed ballots"},
    )
    ax.set_axis_off()
    ax.set_title("Referendum results by region")
    return results


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
