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
    referendum = pd.DataFrame(pd.read_csv('data/referendum.csv',
                                            delimiter=';'))
    regions = pd.DataFrame(pd.read_csv('data/regions.csv',
                                            delimiter=','))
    departments = pd.DataFrame(pd.read_csv('data/departments.csv',
                                            delimiter=','))

    return referendum, regions, departments


def merge_regions_and_departments(regions, departments):
    """Merge regions and departments in one DataFrame.

    The columns in the final DataFrame should be:
    ['code_reg', 'name_reg', 'code_dep', 'name_dep']
    """
    merged_df = pd.merge(left = regions,
                     right = departments,
                     how = 'inner',
                     left_on = 'code',
                     right_on = 'region_code',
                     suffixes = ("_reg", "_dep"),

                     )[['code_reg', 'name_reg', 'code_dep', 'name_dep']]
    return merged_df


def merge_referendum_and_areas(referendum, regions_and_departments):
    """Merge referendum and regions_and_departments in one DataFrame.

    You can drop the lines relative to DOM-TOM-COM departments, and the
    french living abroad, which all have a code that contains `Z`.

    DOM-TOM-COM departments are departements that are remote from metropolitan
    France, like Guadaloupe, Reunion, or Tahiti.
    """
    referendum = referendum.copy()
    referendum = referendum[~referendum['Department code'].str.contains('Z')]
    referendum['Department code'] = (
        referendum['Department code'].astype(str).str.zfill(2)
    )

    regions_and_departments = regions_and_departments.copy()
    mask = ~regions_and_departments['code_dep'].str.contains('Z')
    regions_and_departments = regions_and_departments[mask]
    merged_df = pd.merge(left = referendum,
                        right = regions_and_departments,
                        how = 'left',
                        left_on = 'Department code',
                        right_on = 'code_dep',
                        )

    return merged_df


def compute_referendum_result_by_regions(referendum_and_areas):
    """Return a table with the absolute count for each region.

    The return DataFrame should be indexed by `code_reg` and have columns:
    ['name_reg', 'Registered', 'Abstentions', 'Null', 'Choice A', 'Choice B']
    """
    cols = ['name_reg', 'Registered', 'Abstentions', 'Null', 'Choice A', 'Choice B']
    agg = {'name_reg': 'first',
            'Registered':'sum',
            'Abstentions': 'sum',
            'Null': 'sum',
            'Choice A': 'sum',
            'Choice B': 'sum'
            }
    count_each_region = referendum_and_areas.groupby(
                                                by='code_reg').agg(agg)
    return count_each_region[cols]


def plot_referendum_map(referendum_result_by_regions):
    """Plot a map with the results from the referendum.

    * Load the geographic data with geopandas from `regions.geojson`.
    * Merge these info into `referendum_result_by_regions`.
    * Use the method `GeoDataFrame.plot` to display the result map. The results
      should display the rate of 'Choice A' over all expressed ballots.
    * Return a gpd.GeoDataFrame with a column 'ratio' containing the results.
    """
    gpd_df = gpd.read_file("data/regions.geojson")
    gpd_df.index = gpd_df['code']
    gpd_df = gpd_df.drop(columns='code')
    df_merged = referendum_result_by_regions.join(gpd_df,
                                                  how='inner')
    df_merged['ratio'] = df_merged['Choice A'] / (
                                                    df_merged['Choice A'] +
                                                    df_merged['Choice B']
                                                )
    df_merged = gpd.GeoDataFrame(
                            df_merged,
                            geometry='geometry'
                            )
    df_merged.plot('ratio',
                   legend=True)

    return df_merged


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

    plot_referendum_map(referendum_results)
    plt.show()
