import pandas as pd
import geopandas as gpd
import matplotlib.pyplot as plt
from pathlib import Path


def load_data():
    """Load referendum, regions and departments CSV files."""
    data_dir = Path("data")

    referendum = pd.read_csv(
        data_dir / "referendum.csv",
        sep=";",
    )

    regions = pd.read_csv(
        data_dir / "regions.csv",
    )

    departments = pd.read_csv(
        data_dir / "departments.csv",
    )

    return referendum, regions, departments


def merge_regions_and_departments(regions, departments):
    """Merge regions and departments into one DataFrame.

    Returns
    -------
    pandas.DataFrame
        Columns: code_reg, name_reg, code_dep, name_dep.
    """
    regions = regions.rename(columns={"code": "code_reg", "name": "name_reg"})
    departments = departments.rename(
        columns={
            "region_code": "code_reg",
            "code": "code_dep",
            "name": "name_dep",
        }
    )

    regions["code_reg"] = regions["code_reg"].astype(str)
    departments["code_reg"] = departments["code_reg"].astype(str)
    departments["code_dep"] = departments["code_dep"].astype(str).str.zfill(2)

    regions_and_departments = departments.merge(
        regions[["code_reg", "name_reg"]],
        on="code_reg",
        how="left",
    )

    return regions_and_departments[
        ["code_reg", "name_reg", "code_dep", "name_dep"]
    ]


def merge_referendum_and_areas(referendum, regions_and_departments):
    """Merge referendum results with geographical information.

    Excludes overseas departments and French citizens living abroad,
    identified by department codes containing Z.
    """
    referendum = referendum.copy()
    regions_and_departments = regions_and_departments.copy()

    referendum["code_dep"] = referendum["Department code"].astype(str).str.zfill(2)
    regions_and_departments["code_dep"] = (
        regions_and_departments["code_dep"].astype(str).str.zfill(2)
    )

    referendum = referendum[
        ~referendum["code_dep"].str.contains("Z", na=False)
    ]

    regions_and_departments = regions_and_departments[
        ~regions_and_departments["code_dep"].str.contains(
            "Z", na=False
        )
    ].drop(columns=["name_dep"])

    merged = referendum.merge(
        regions_and_departments,
        on="code_dep",
        how="inner",
    )
    merged["name_dep"] = merged["Department name"]

    return merged[
        [
            "Department code",
            "Department name",
            "Town code",
            "Town name",
            "Registered",
            "Abstentions",
            "Null",
            "Choice A",
            "Choice B",
            "code_dep",
            "code_reg",
            "name_reg",
            "name_dep",
        ]
    ]


def compute_referendum_result_by_regions(referendum_and_areas):
    """Aggregate referendum results by region.

    Returns
    -------
    pandas.DataFrame
        Indexed by code_reg, with columns:
        name_reg, Registered, Abstentions, Null, Choice A, Choice B.
    """
    result = (
        referendum_and_areas
        .groupby("code_reg")
        .agg(
            name_reg=("name_reg", "first"),
            Registered=("Registered", "sum"),
            Abstentions=("Abstentions", "sum"),
            Null=("Null", "sum"),
            **{
                "Choice A": ("Choice A", "sum"),
                "Choice B": ("Choice B", "sum"),
            },
        )
    )

    return result


def plot_referendum_map(referendum_result_by_regions):
    """Plot the proportion of votes for Choice A on a map.

    Returns
    -------
    geopandas.GeoDataFrame
        Geographical data with a ratio column.
    """
    # Load geographical information.
    geojson_path = Path("data/regions.geojson")

    if not geojson_path.exists():
        geojson_path = Path("regions.geojson")

    regions_map = gpd.read_file(geojson_path)
    regions_map = regions_map.rename(columns={"code": "code_reg", "nom": "name_reg"})

    # Make sure the geographical region codes are strings.
    regions_map["code_reg"] = regions_map["code_reg"].astype(str)
    regions_map = regions_map.drop(columns=["name_reg"])

    # Merge referendum results with geographical data.
    referendum_map = regions_map.merge(
        referendum_result_by_regions.reset_index(),
        on="code_reg",
        how="left",
    )

    # Calculate the proportion of votes for Choice A.
    expressed_votes = (
        referendum_map["Choice A"] + referendum_map["Choice B"]
    )

    referendum_map["ratio"] = (
        referendum_map["Choice A"] / expressed_votes
    )

    # Plot the map.
    fig, ax = plt.subplots(figsize=(12, 10))

    referendum_map.plot(
        column="ratio",
        cmap="RdYlGn",
        linewidth=0.8,
        edgecolor="white",
        legend=True,
        vmin=0,
        vmax=1,
        missing_kwds={
            "color": "lightgrey",
            "label": "No data",
        },
        legend_kwds={
            "label": "Share of votes for Choice A",
            "orientation": "horizontal",
            "shrink": 0.7,
        },
        ax=ax,
    )

    ax.set_title(
        "Referendum results by region",
        fontsize=16,
        fontweight="bold",
    )

    ax.axis("off")

    plt.tight_layout()

    return referendum_map


if __name__ == "__main__":

    referendum, df_reg, df_dep = load_data()

    regions_and_departments = merge_regions_and_departments(
        df_reg,
        df_dep,
    )

    referendum_and_areas = merge_referendum_and_areas(
        referendum,
        regions_and_departments,
    )

    referendum_results = compute_referendum_result_by_regions(
        referendum_and_areas,
    )

    print(referendum_results)

    plot_referendum_map(referendum_results)

    plt.show()
