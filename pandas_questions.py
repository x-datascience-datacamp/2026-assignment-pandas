
"""Plotting referendum results in pandas."""

import pandas as pd
import geopandas as gpd
import matplotlib.pyplot as plt


def load_data():
    """Load referendum, regions and departments data."""
    referendum = pd.read_csv("data/referendum.csv", sep=";")
    regions = pd.read_csv("data/regions.csv")
    departments = pd.read_csv("data/departments.csv")

    return referendum, regions, departments


def merge_regions_and_departments(regions, departments):
    """Merge regions and departments into one DataFrame."""

    regions = regions.rename(
        columns={
            "code": "code_reg",
            "name": "name_reg",
        }
    )

    departments = departments.rename(
        columns={
            "code": "code_dep",
            "name": "name_dep",
        }
    )

    # Find the department column identifying its region.
    if "region_code" in departments.columns:
        departments["code_reg"] = departments["region_code"]
    elif "region" in departments.columns:
        departments["code_reg"] = departments["region"]
    elif "region_code" not in departments.columns:
        departments["code_reg"] = departments["region_id"].map(
            regions.set_index("id")["code_reg"]
        )

    departments["code_reg"] = departments["code_reg"].astype(str)
    regions["code_reg"] = regions["code_reg"].astype(str)

    result = pd.merge(
        departments,
        regions,
        on="code_reg",
        how="inner",
    )

    return result[
        ["code_reg", "name_reg", "code_dep", "name_dep"]
    ]


def merge_referendum_and_areas(referendum, regions_and_departments):
    """Merge referendum results with geographical information."""

    referendum = referendum.copy()
    regions_and_departments = regions_and_departments.copy()

    # Remove overseas territories and French citizens abroad.
    referendum = referendum[
        ~referendum["Department code"].astype(str).str.contains("Z")
    ]

    # Harmonize department codes.
    referendum["Department code"] = (
        referendum["Department code"].astype(str).str.zfill(2)
    )

    regions_and_departments["code_dep"] = (
        regions_and_departments["code_dep"].astype(str).str.zfill(2)
    )

    result = pd.merge(
        referendum,
        regions_and_departments,
        left_on="Department code",
        right_on="code_dep",
        how="inner",
    )

    return result.dropna()


def compute_referendum_result_by_regions(referendum_and_areas):
    """Compute absolute referendum results for each region."""

    columns_to_sum = [
        "Registered",
        "Abstentions",
        "Null",
        "Choice A",
        "Choice B",
    ]

    result = referendum_and_areas.groupby(
        ["code_reg", "name_reg"]
    )[columns_to_sum].sum()

    result = result.reset_index(level="name_reg")

    return result[
        ["name_reg"] + columns_to_sum
    ]


def plot_referendum_map(referendum_result_by_regions):
    """Plot the proportion of Choice A votes by region."""

    regions_geo = gpd.read_file("data/regions.geojson")

    results = referendum_result_by_regions.reset_index()

    # Harmonize region codes.
    regions_geo["code"] = (
        regions_geo["code"].astype(str).str.zfill(2)
    )

    results["code_reg"] = (
        results["code_reg"].astype(str).str.zfill(2)
    )

    gdf = regions_geo.merge(
        results,
        left_on="code",
        right_on="code_reg",
        how="inner",
    )

    # Calculate Choice A among expressed ballots.
    gdf["ratio"] = (
        gdf["Choice A"]
        / (gdf["Choice A"] + gdf["Choice B"])
    )

    gdf.plot(
        column="ratio",
        legend=True,
        cmap="Blues",
        figsize=(12, 8),
        edgecolor="black",
    )

    plt.title("Referendum results by region - Choice A")
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
