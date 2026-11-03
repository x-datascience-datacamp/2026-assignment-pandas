
import pandas as pd
import geopandas as gpd
import matplotlib.pyplot as plt


def load_data():
    """Load data from the CSV files referundum/regions/departments."""
    referendum = pd.read_csv("data/referendum.csv", sep=';')
    regions = pd.read_csv("data/regions.csv")
    departments = pd.read_csv("data/departments.csv")
    return referendum, regions, departments


def merge_regions_and_departments(regions, departments):
    """Merge regions and departments in one DataFrame.

    The columns in the final DataFrame should be:
    ['code_reg', 'name_reg', 'code_dep', 'name_dep']
    """
    regions_renamed = regions.rename(
        columns={"code": "code_reg", "name": "name_reg"}
    )
    regions_renamed = regions_renamed[['code_reg', 'name_reg']]

    departements_renamed = departments.rename(
        columns={"code": "code_dep", "name": "name_dep"}
    )
    departements_renamed = departements_renamed[
        ['code_dep', 'name_dep', 'region_code']
    ]

    merged = regions_renamed.merge(
        departements_renamed,
        left_on='code_reg',
        right_on='region_code',
        how='inner'
    )

    return merged[['code_reg', 'name_reg', 'code_dep', 'name_dep']]


def merge_referendum_and_areas(referendum, regions_and_departments):
    """Merge referendum and regions_and_departments in one DataFrame.

    You can drop the lines relative to DOM-TOM-COM departments, and the
    french living abroad, which all have a code that contains `Z`.
    """
    mask = referendum['Department code'].astype(str).str.contains(
        'Z', na=False
    )

    referendum_simplified = referendum[~mask]
    referendum_simplified = referendum_simplified.copy()

    referendum_simplified['Department code'] = (
        referendum_simplified['Department code'].astype(str)
    )
    referendum_simplified['Department code'] = (
        referendum_simplified['Department code'].str.zfill(2)
    )

    merged = referendum_simplified.merge(
        regions_and_departments,
        left_on='Department code',
        right_on='code_dep',
        how='inner'
    )

    return merged


def compute_referendum_result_by_regions(referendum_and_areas):
    """Return a table with the absolute count for each region."""

    columns = [
        'Registered',
        'Abstentions',
        'Null',
        'Choice A',
        'Choice B'
    ]

    result = (
        referendum_and_areas
        .groupby(['code_reg', 'name_reg'], as_index=False)[columns]
        .sum()
        .set_index('code_reg')
        .loc[:, ['name_reg'] + columns]
    )

    return result


def plot_referendum_map(referendum_result_by_regions):
    """Plot a map with the results from the referendum."""

    regions_geo = gpd.read_file('data/regions.geojson')

    results = referendum_result_by_regions.copy()

    # Ratio : Choice A sur l'ensemble des bulletins exprimés (A + B)
    results['ratio'] = (
        results['Choice A'] /
        (results['Choice A'] + results['Choice B'])
    )

    merged = regions_geo.merge(
        results,
        left_on='code',
        right_index=True,
        how='inner'
    )

    merged = gpd.GeoDataFrame(merged, geometry='geometry')

    merged.plot(
        column='ratio',
        legend=True,
        cmap='RdBu',
        edgecolor='black'
    )

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
