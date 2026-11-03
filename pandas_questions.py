
"""Plot referendum results by French region using pandas and geopandas."""

from pathlib import Path

import geopandas as gpd
import matplotlib.pyplot as plt
import pandas as pd


DATA_DIR = Path(__file__).resolve().parent / "data"


def load_data():
    """Load the referendum, region, and department CSV files."""
    referendum = pd.read_csv(
        DATA_DIR / "referendum.csv",
        sep=";",
        dtype={"Department code": str},
    )
    regions = pd.read_csv(
        DATA_DIR / "regions.csv",
        dtype={"code": str},
    )
    departments = pd.read_csv(
        DATA_DIR / "departments.csv",
        dtype={"region_code": str, "code": str},
    )
    return referendum, regions, departments


def merge_regions_and_departments(regions, departments):
    """Associate departments with their regions."""
    merged = departments.merge(
        regions,
        left_on="region_code",
        right_on="code",
        how="inner",
        suffixes=("_dep", "_reg"),
    )
    return merged[["code_reg", "name_reg", "code_dep", "name_dep"]]


def merge_referendum_and_areas(referendum, regions_and_departments):
    """Match each metropolitan commune with its department and region."""
    referendum = referendum.copy()
    referendum["Department code"] = (
        referendum["Department code"].astype(str).str.zfill(2)
    )
    referendum = referendum.loc[
        ~referendum["Department code"].str.contains("Z", regex=False)
    ]
    merged = referendum.merge(
        regions_and_departments,
        left_on="Department code",
        right_on="code_dep",
        how="inner",
    )
    return merged.dropna()


def compute_referendum_result_by_regions(referendum_and_areas):
    """Sum referendum counts across communes for each region."""
    columns = [
        "Registered",
        "Abstentions",
        "Null",
        "Choice A",
        "Choice B",
    ]
    result = referendum_and_areas.groupby(
        ["code_reg", "name_reg"], as_index=False
    )[columns].sum()
    return result.set_index("code_reg")


def plot_referendum_map(referendum_result_by_regions):
    """Map the regional share of Choice A among expressed votes."""
    regions = gpd.read_file(DATA_DIR / "regions.geojson")
    regions = regions.rename(columns={"code": "code_reg"})
    result = regions.merge(
        referendum_result_by_regions.reset_index(),
        on="code_reg",
        how="inner",
    )
    result["ratio"] = result["Choice A"] / (
        result["Choice A"] + result["Choice B"]
    )

    fig, ax = plt.subplots(figsize=(11, 8))
    result.plot(
        column="ratio",
        cmap="RdYlBu",
        legend=True,
        edgecolor="white",
        linewidth=0.6,
        ax=ax,
    )
    ax.set_title("Share of Choice A by region", fontsize=15)
    ax.set_axis_off()
    fig.tight_layout()
    return result


if __name__ == "__main__":
    referendum, df_reg, df_dep = load_data()
    regions_and_departments = merge_regions_and_departments(df_reg, df_dep)
    referendum_and_areas = merge_referendum_and_areas(
        referendum, regions_and_departments
    )
    referendum_results = compute_referendum_result_by_regions(
        referendum_and_areas
    )
    print(referendum_results)
    plot_referendum_map(referendum_results)
    plt.show()
