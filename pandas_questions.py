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
    referendum = pd.read_csv('./data/referendum.csv', sep=';')
    regions = pd.read_csv('./data/regions.csv')
    departments = pd.read_csv('./data/departments.csv')

    return referendum, regions, departments


def merge_regions_and_departments(regions, departments):
    """Merge regions and departments in one DataFrame.

    The columns in the final DataFrame should be:
    ['code_reg', 'name_reg', 'code_dep', 'name_dep']
    """
    reg_df = regions.rename(columns={'code': 'code_reg', 'name': 'name_reg'})
    dep_df = departments.rename(columns={
        'region_code': 'code_reg',
        'code': 'code_dep',
        'name': 'name_dep'
    })
    dep_df['code_dep'] = dep_df['code_dep'].astype(str).str.zfill(2)
    regions_and_departments = pd.merge(reg_df, dep_df, on='code_reg')
    cols = ["code_reg", "name_reg", "code_dep", "name_dep"]
    regions_and_departments = regions_and_departments[cols]

    return regions_and_departments


def merge_referendum_and_areas(referendum, regions_and_departments):
    """Merge referendum and regions_and_departments in one DataFrame.

    You can drop the lines relative to DOM-TOM-COM departments, and the
    french living abroad, which all have a code that contains `Z`.

    DOM-TOM-COM departments are departements that are remote from metropolitan
    France, like Guadaloupe, Reunion, or Tahiti.
    """
    ref_df = referendum.copy()
    ref_df['code_dep'] = ref_df['Department code'].astype(str).str.zfill(2)
    mask = ref_df['code_dep'].astype(str).str.contains('Z')
    ref_df = ref_df.loc[~mask]
    referendum_and_areas = pd.merge(ref_df, regions_and_departments, on='code_dep')

    return referendum_and_areas


def compute_referendum_result_by_regions(referendum_and_areas):
    """Return a table with the absolute count for each region.

    The return DataFrame should be indexed by `code_reg` and have columns:
    ['name_reg', 'Registered', 'Abstentions', 'Null', 'Choice A', 'Choice B']
    """
    numeric_cols = ['Registered', 'Abstentions', 'Null', 'Choice A', 'Choice B']
    grouped = referendum_and_areas.groupby(['code_reg', 'name_reg'])[numeric_cols].sum()
    result = grouped.reset_index(level='name_reg')
    cols = ["name_reg", "Registered", "Abstentions", "Null", "Choice A", "Choice B"]
    result = result[cols]

    return result


def plot_referendum_map(referendum_result_by_regions):
    """Plot a map with the results from the referendum.

    * Load the geographic data with geopandas from `regions.geojson`.
    * Merge these info into `referendum_result_by_regions`.
    * Use the method `GeoDataFrame.plot` to display the result map. The results
      should display the rate of 'Choice A' over all expressed ballots.
    * Return a gpd.GeoDataFrame with a column 'ratio' containing the results.
    """
    expressed_votes = (
        referendum_result_by_regions["Choice A"]
        + referendum_result_by_regions["Choice B"]
    )
    referendum_result_by_regions['ratio'] = (
        referendum_result_by_regions['Choice A'] / expressed_votes
    )

    gdf_regions = gpd.read_file('./data/regions.geojson')
    right_on_col = 'code_reg' if 'code_reg' in gdf_regions.columns else 'code'
    merged_gdf = gdf_regions.merge(
        referendum_result_by_regions,
        left_on=right_on_col,
        right_index=True
    )

    fig, ax = plt.subplots(1, 1, figsize=(10, 10))
    merged_gdf.plot(
        column='ratio',
        legend=True,
        cmap='RdYlBu',
        ax=ax,
        legend_kwds={'label': "rate of 'Choice A'"}
    )
    ax.set_axis_off()
    plt.title("referendum results by region")

    return gpd.GeoDataFrame(merged_gdf)


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
