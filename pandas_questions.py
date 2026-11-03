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
    # referendum = pd.DataFrame({})
    # regions = pd.DataFrame({})
    # departments = pd.DataFrame({})


    referendum = pd.read_csv('./data/referendum.csv', sep=';')
    # print(referendum.head(5))
    regions = pd.read_csv('./data/regions.csv')
    # print(regions.head(5))
    departments = pd.read_csv('./data/departments.csv')
    # print(departments.head(5))


    return referendum, regions, departments


def merge_regions_and_departments(regions, departments):
    """Merge regions and departments in one DataFrame.

    The columns in the final DataFrame should be:
    ['code_reg', 'name_reg', 'code_dep', 'name_dep']
    """

    # print('region.shape', regions.shape)
    # print('departments.shape', departments.shape)

    # print(len(regions) + len(departments))

    # print(
    #     'code & region_code before merging',
    #     regions['code'].unique(),
    #     departments['region_code'].unique()
    # )

    results = pd.merge(
        left=regions,
        right=departments,
        how='inner',
        left_on='code',
        right_on='region_code',
        suffixes=('_reg', '_dep')
    )

    # print(results.shape)
    # print(results.columns)
    # print(results[['code_reg', 'name_reg', 'code_dep', 'name_dep']].columns)


    return results[['code_reg', 'name_reg', 'code_dep', 'name_dep']] # pd.DataFrame({})


def merge_referendum_and_areas(referendum, regions_and_departments):
    """Merge referendum and regions_and_departments in one DataFrame.

    You can drop the lines relative to DOM-TOM-COM departments, and the
    french living abroad, which all have a code that contains `Z`.

    DOM-TOM-COM departments are departements that are remote from metropolitan
    France, like Guadaloupe, Reunion, or Tahiti.
    """

    # Overseas departments and regions (DROM)
    drom = [
        "Guadeloupe", "Martinique", "Guyane",
        "La Réunion", "Mayotte"
    ]

    # Overseas collectivities (COM)
    com = [
        "Saint-Pierre-et-Miquelon", "Saint-Barthélemy",
        "Saint-Martin", "Wallis et Futuna",
        "Polynésie française"
    ]

    # Other overseas territories with special statuses
    other = []
    # [
    #     "Terres australes et antarctiques françaises",
    #     "Nouvelle-Calédonie", "Île de Clipperton"
    # ]

    # Keep only metropolitan departments
    overseas = drom + com + other

    regions_and_departments = regions_and_departments[
        ~regions_and_departments["name_dep"].isin(overseas)
    ]

    print('referendum.shape', referendum.shape)
    print('regions_and_departments.shape', regions_and_departments.shape)

    print(len(referendum) + len(regions_and_departments))



    referendum = referendum[
        ~referendum['Department code'].str.contains('Z')
    ]

    # print('referendum & regions_and_departments before merging',
    #     sorted(referendum['Department code'].unique()),
    #     sorted(regions_and_departments['code_dep'].unique())
    # )

    referendum["Department code"] = referendum["Department code"].str.zfill(2)

    results = pd.merge(
        left=referendum,
        right=regions_and_departments,
        how='inner',
        left_on='Department code',
        right_on='code_dep',
        suffixes=('_ref', '_reg')
    )
    print('after merging', results.shape)
    print('after mergin columns', results.columns)
    # print(results[['code_reg', 'name_reg', 'code_dep', 'name_dep']].columns)




    return results[[
        'Department code', 'Department name', 'Town code', 'Town name',
        'Registered', 'Abstentions', 'Null', 'Choice A', 'Choice B',
        'code_dep', 'code_reg', 'name_reg', 'name_dep'
    ]] # pd.DataFrame({})


def compute_referendum_result_by_regions(referendum_and_areas):
    """Return a table with the absolute count for each region.

    The return DataFrame should be indexed by `code_reg` and have columns:
    ['name_reg', 'Registered', 'Abstentions', 'Null', 'Choice A', 'Choice B']
    """
    print(referendum_and_areas)

    counting = referendum_and_areas.groupby(
        ["code_reg", "name_reg"]
    )[['Registered', 'Abstentions', 'Null', 'Choice A', 'Choice B']].sum()
    # print('count count', counting.columns)
    # print(counting)
    # print('count count',
    #     counting[
    #         ['name_reg', 'Registered', 'Abstentions', 'Null', 'Choice A', 'Choice B']
    #     ].columns
    # )

    # print("==============")
    # print(counting)
    # print("==============")
    # print(counting.reset_index(level="name_reg"))
    # print("==============")


    return counting.reset_index(level="name_reg")


def plot_referendum_map(referendum_result_by_regions):
    """Plot a map with the results from the referendum.

    * Load the geographic data with geopandas from `regions.geojson`.
    * Merge these info into `referendum_result_by_regions`.
    * Use the method `GeoDataFrame.plot` to display the result map. The results
      should display the rate of 'Choice A' over all expressed ballots.
    * Return a gpd.GeoDataFrame with a column 'ratio' containing the results.
    """

    # return gpd.GeoDataFrame({})

    regions_geo = gpd.read_file("data/regions.geojson")

    with pd.option_context('display.max_columns', None):
        print(referendum_result_by_regions.head(3))

    with pd.option_context('display.max_columns', None):
        print(regions_geo.head(3))

    merged_regions_geo = pd.merge(
        regions_geo,
        referendum_result_by_regions,
        left_on='code',
        right_on='code_reg'
    )

    merged_regions_geo['ratio'] = merged_regions_geo['Choice A'] /\
        (merged_regions_geo['Choice A']  + merged_regions_geo['Choice B'])

    merged_regions_geo.plot(
        column="ratio",
        legend=True,
    )

    return merged_regions_geo

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
