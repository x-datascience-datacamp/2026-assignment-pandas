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
    departement_file = "data/departments.csv"
    region_file = "data/regions.csv"
    referendum_file = "data/referendum.csv"

    referendum = pd.DataFrame({})
    regions = pd.DataFrame({})
    departments = pd.DataFrame({})

    referendum = pd.read_csv(referendum_file, sep=';')
    regions = pd.read_csv(region_file)
    departments = pd.read_csv(departement_file)

    return referendum, regions, departments


def merge_regions_and_departments(regions, departments):
    """Merge regions and departments in one DataFrame.

    The columns in the final DataFrame should be:
    ['code_reg', 'name_reg', 'code_dep', 'name_dep']
    """
    df = pd.DataFrame({})


    df = pd.merge(regions, departments, left_on='code', right_on='region_code')
    df.rename(columns={'code_x': 'code_reg', 'name_x': 'name_reg',
                       'code_y': 'code_dep', 'name_y': 'name_dep'}, inplace=True)
    df.drop(columns=['id_y', 'slug_x','slug_y','region_code','id_x'], inplace=True)



    return df


def merge_referendum_and_areas(referendum, regions_and_departments):
    """Merge referendum and regions_and_departments in one DataFrame.

    You can drop the lines relative to DOM-TOM-COM departments, and the
    french living abroad, which all have a code that contains `Z`.

    DOM-TOM-COM departments are departements that are remote from metropolitan
    France, like Guadaloupe, Reunion, or Tahiti.
    """
    referendum['Department code'] = (
        referendum['Department code'].astype(str).str.zfill(2)
    )
    regions_and_departments['code_dep'] = (
        regions_and_departments['code_dep'].astype(str).str.zfill(2)
    )

    referendum = referendum[
        ~referendum['Department code'].str.contains('Z', na=False)
    ]

    df = pd.merge(
        referendum,
        regions_and_departments,
        left_on='Department code',
        right_on='code_dep'
    )

    return df


def compute_referendum_result_by_regions(referendum_and_areas):
    """Return a table with the absolute count for each region.

    The return DataFrame should be indexed by `code_reg` and have columns:
    ['name_reg', 'Registered', 'Abstentions', 'Null', 'Choice A', 'Choice B']
    """
    df = referendum_and_areas.groupby('code_reg').agg({
        'name_reg': 'first',
        'Registered': 'sum',
        'Abstentions': 'sum',
        'Null': 'sum',
        'Choice A': 'sum',
        'Choice B': 'sum'
    })
    return df


def plot_referendum_map(referendum_result_by_regions):
    """Plot a map with the results from the referendum.

    * Load the geographic data with geopandas from `regions.geojson`.
    * Merge these info into `referendum_result_by_regions`.
    * Use the method `GeoDataFrame.plot` to display the result map. The results
      should display the rate of 'Choice A' over all expressed ballots.
    * Return a gpd.GeoDataFrame with a column 'ratio' containing the results.
    """
    # Load the geographic data
    gdf = gpd.read_file('data/regions.geojson')

    # Merge the geographic data with the referendum results
    gdf = pd.merge(
        gdf,
        referendum_result_by_regions,
        left_on='code',
        right_on='code_reg'
    )

    # Compute the ratio of 'Choice A' over all expressed ballots
    gdf['ratio'] = gdf['Choice A'] / (
        gdf['Registered'] - gdf['Abstentions'] - gdf['Null']
    )

    # Plot the map
    gdf.plot(column='ratio', cmap='coolwarm', legend=True, edgecolor='black')

    return gpd.GeoDataFrame(gdf, geometry='geometry', crs=gdf.crs)


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
