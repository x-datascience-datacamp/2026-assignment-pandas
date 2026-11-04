
"""Plotting referendum results in pandas."""

import pandas as pd
import geopandas as gpd
import matplotlib.pyplot as plt


def load_data():
    """Load data from the CSV files referendum/regions/departments."""

    referendum = pd.read_csv(
        "data/referendum.csv",
        sep=";",
        dtype={"Department code": str}
    )

    regions = pd.read_csv(
        "data/regions.csv",
        sep=",",
        dtype={"code": str}
    )

    departments = pd.read_csv(
        "data/departments.csv",
        sep=",",
        dtype={"code": str, "region_code": str}
    )

    return referendum, regions, departments


def normalize_department_code(series):
    """Normalize department codes to make joins reliable."""
    return (
        series.astype(str)
        .str.strip()
        .str.zfill(2)
    )


def merge_regions_and_departments(regions, departments):
    """Merge regions and departments in one DataFrame."""

    regions = regions.rename(columns={
        "code": "code_reg",
        "name": "name_reg"
    }).copy()

    departments = departments.rename(columns={
        "region_code": "code_reg",
        "code": "code_dep",
        "name": "name_dep"
    }).copy()

    departments["code_dep"] = normalize_department_code(
        departments["code_dep"]
    )

    departments["code_reg"] = departments["code_reg"].astype(str).str.strip()
    regions["code_reg"] = regions["code_reg"].astype(str).str.strip()

    regions_and_departments = departments.merge(
        regions[["code_reg", "name_reg"]],
        on="code_reg",
        how="left"
    )

    return regions_and_departments[
        ["code_reg", "name_reg", "code_dep", "name_dep"]
    ]


def merge_referendum_and_areas(referendum, regions_and_departments):
    """Merge referendum results with geographical information."""

    referendum = referendum.copy()

    # Keep the original column and create a normalized join key.
    referendum["code_dep"] = normalize_department_code(
        referendum["Department code"]
    )

    # Remove DOM-TOM-COM departments and French citizens abroad.
    referendum = referendum[
        ~referendum["code_dep"].str.contains("Z", na=False)
    ].copy()

    regions_and_departments = regions_and_departments.copy()
    regions_and_departments["code_dep"] = normalize_department_code(
        regions_and_departments["code_dep"]
    )

    # Merge referendum results with geographical information.
    referendum_and_areas = referendum.merge(
        regions_and_departments,
        on="code_dep",
        how="inner"
    )

    return referendum_and_areas


def compute_referendum_result_by_regions(referendum_and_areas):
    """Aggregate referendum results by region."""

    referendum_result_by_regions = (
        referendum_and_areas
        .groupby("code_reg")
        .agg(
            name_reg=("name_reg", "first"),
            Registered=("Registered", "sum"),
            Abstentions=("Abstentions", "sum"),
            Null=("Null", "sum"),
            **{
                "Choice A": ("Choice A", "sum"),
                "Choice B": ("Choice B", "sum")
            }
        )
    )

    return referendum_result_by_regions[
        [
            "name_reg",
            "Registered",
            "Abstentions",
            "Null",
            "Choice A",
            "Choice B"
        ]
    ]


def plot_referendum_map(referendum_result_by_regions):
    """Plot a map with the results from the referendum."""

    regions_map = gpd.read_file("data/regions.geojson")

    # Rename the geographical code column.
    if "code" in regions_map.columns:
        regions_map = regions_map.rename(
            columns={"code": "code_reg"}
        )

    regions_map["code_reg"] = (
        regions_map["code_reg"].astype(str).str.strip()
    )

    # The aggregation uses code_reg as its index.
    results = referendum_result_by_regions.reset_index()

    map_data = regions_map.merge(
        results,
        on="code_reg",
        how="left"
    )

    # Calculate the share of Choice A among expressed votes.
    expressed_votes = map_data["Choice A"] + map_data["Choice B"]

    map_data["ratio"] = (
        map_data["Choice A"] / expressed_votes
    )

    # Plot the map.
    fig, ax = plt.subplots(figsize=(12, 12))

    map_data.plot(
        column="ratio",
        cmap="Reds",
        linewidth=0.8,
        edgecolor="white",
        legend=True,
        legend_kwds={
            "label": "Percentage of votes for Choice A",
            "orientation": "horizontal",
            "shrink": 0.7
        },
        missing_kwds={
            "color": "lightgrey",
            "label": "No data"
        },
        ax=ax,
        vmin=0,
        vmax=1
    )

    ax.set_title(
        "Referendum results by region\nShare of votes for Choice A",
        fontsize=16,
        fontweight="bold"
    )

    ax.axis("off")
    plt.tight_layout()

    plt.savefig(
        "referendum_map.png",
        dpi=300,
        bbox_inches="tight"
    )

    return map_data


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
