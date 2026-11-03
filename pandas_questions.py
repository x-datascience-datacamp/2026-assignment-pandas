import geopandas as gpd
import matplotlib.pyplot as plt
import pandas as pd


def load_data():
    referendum = pd.read_csv("data/referendum.csv", sep=None, engine="python")
    regions = pd.read_csv("data/regions.csv", sep=None, engine="python")
    departments = pd.read_csv("data/departments.csv", sep=None, engine="python")

    return referendum, regions, departments


def merge_regions_and_departments(regions, departments):
    merged = pd.merge(
        regions,
        departments,
        left_on="code",
        right_on="region_code",
    )

    merged = merged.rename(
        columns={
            "code_x": "code_reg",
            "name_x": "name_reg",
            "code_y": "code_dep",
            "name_y": "name_dep",
        }
    )

    return merged[["code_reg", "name_reg", "code_dep", "name_dep"]]


def merge_referendum_and_areas(referendum, regions_and_departments):
    referendum = referendum.copy()
    areas = regions_and_departments.copy()

    def normalize_code(code):
        code = str(code).strip()
        if code.isdigit():
            return str(int(code))
        return code

    referendum["Department code"] = referendum["Department code"].map(
        normalize_code
    )
    areas["code_dep"] = areas["code_dep"].map(normalize_code)

    referendum = referendum[
        ~referendum["Department code"].str.contains("Z", na=False)
    ]

    return pd.merge(
        referendum,
        areas,
        left_on="Department code",
        right_on="code_dep",
    )


def compute_referendum_result_by_regions(referendum_and_areas):
    columns_to_sum = [
        "Registered",
        "Abstentions",
        "Null",
        "Choice A",
        "Choice B",
    ]

    result = referendum_and_areas.groupby("code_reg").agg(
        name_reg=("name_reg", "first"),
        **{
            column: (column, "sum")
            for column in columns_to_sum
        },
    )

    return result[
        [
            "name_reg",
            "Registered",
            "Abstentions",
            "Null",
            "Choice A",
            "Choice B",
        ]
    ]


def plot_referendum_map(referendum_result_by_regions):
    regions_map = gpd.read_file("data/regions.geojson")

    regions_map["code"] = regions_map["code"].astype(str)

    results = referendum_result_by_regions.copy()
    results.index = results.index.astype(str)

    regions_map = regions_map.merge(
        results,
        left_on="code",
        right_index=True,
    )

    total_expressed = (
        regions_map["Choice A"] + regions_map["Choice B"]
    )

    regions_map["ratio"] = regions_map["Choice A"] / total_expressed

    regions_map.plot(
        column="ratio",
        cmap="RdYlGn",
        legend=True,
        edgecolor="black",
        linewidth=0.5,
        figsize=(12, 8),
    )

    plt.title("Referendum results - Choice A")
    plt.axis("off")

    return regions_map


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
