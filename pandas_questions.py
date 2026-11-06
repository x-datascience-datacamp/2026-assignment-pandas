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
    referendum = pd.read_csv("data/referendum.csv",sep=';')
    regions = pd.read_csv("data/regions.csv")
    departments = pd.read_csv("data/departments.csv")

    return referendum, regions, departments


def merge_regions_and_departments(regions, departments):
    """Merge regions and departments in one DataFrame.

    The columns in the final DataFrame should be:
    ['code_reg', 'name_reg', 'code_dep', 'name_dep']
    """

    regions=regions.rename(columns={'code': 'code_reg','name':'name_reg'})
    departments=departments.rename(columns={'region_code': 'code_reg',
                                            'code':"code_dep",'name':'name_dep'})

    df_final=pd.merge(regions,departments,on="code_reg")
    df_final=df_final[['code_reg', 'name_reg', 'code_dep', 'name_dep']]
    return df_final


def merge_referendum_and_areas(referendum, regions_and_departments):
    """Merge referendum and regions_and_departments in one DataFrame.

    You can drop the lines relative to DOM-TOM-COM departments, and the
    french living abroad, which all have a code that contains `Z`.

    DOM-TOM-COM departments are departements that are remote from metropolitan
    France, like Guadaloupe, Reunion, or Tahiti.
    """

    referendum=referendum[~referendum['Department code'].str.contains('Z')]

    referendum=referendum.rename(columns={'Department code': 'code_dep'})
    regions_and_departments['code_dep']=regions_and_departments['code_dep'].replace(
        to_replace=r'^0+(?=\d)',
        value='', regex=True)
    df_final=pd.merge(referendum,regions_and_departments,on="code_dep")
    df_final['Department code']=df_final['code_dep']

    return df_final


def compute_referendum_result_by_regions(referendum_and_areas):
    """Return a table with the absolute count for each region.

    The return DataFrame should be indexed by `code_reg` and have columns:
    ['name_reg', 'Registered', 'Abstentions', 'Null', 'Choice A', 'Choice B']
    """

    cols=['Registered', 'Abstentions', 'Null', 'Choice A', 'Choice B']
    df_grp_by=referendum_and_areas.groupby(["name_reg"],as_index=False)[cols].sum()

    return df_grp_by


def plot_referendum_map(referendum_result_by_regions):
    """Plot a map with the results from the referendum.

    * Load the geographic data with geopandas from `regions.geojson`.
    * Merge these info into `referendum_result_by_regions`.
    * Use the method `GeoDataFrame.plot` to display the result map. The results
      should display the rate of 'Choice A' over all expressed ballots.
    * Return a gpd.GeoDataFrame with a column 'ratio' containing the results.
    """

    geo_map1=gpd.read_file("data/regions.geojson")

    geo_map1=geo_map1.rename(columns={'nom': 'name_reg'})
    geo_map2=pd.merge(geo_map1,referendum_result_by_regions,on="name_reg")
    geo_map2['ratio']=geo_map2['Choice A']/(geo_map2['Choice A']+geo_map2['Choice B'])
    geo_map2.drop(columns=['Registered', 'Abstentions', 'Null', 'Choice A', 'Choice B'])
    geo_map2.plot(column="ratio",legend=True)
    return geo_map2


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



# referendum, regions, departments=load_data()


# df_merge1=merge_regions_and_departments(regions, departments)

# df_merge1.to_csv("df_merge1.csv")

# df_merge2=merge_referendum_and_areas(referendum, regions_and_departments=df_merge1)
# df_merge2.to_csv("df_merge2.csv")

# df_merge3=compute_referendum_result_by_regions(referendum_and_areas)
# df_merge3.to_csv("df_merge3.csv")
