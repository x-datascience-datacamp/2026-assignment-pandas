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
    referendum = pd.read_csv("data/referendum.csv", sep = ";")
    regions = pd.read_csv("data/regions.csv")
    departments = pd.read_csv("data/departments.csv")
    return referendum, regions, departments


def merge_regions_and_departments(regions, departments):
    """Merge regions and departments in one DataFrame.

    The columns in the final DataFrame should be:
    ['code_reg', 'name_reg', 'code_dep', 'name_dep']
    """
    merge = pd.merge(left = regions, right = departments,
                     left_on = 'code', right_on = 'region_code', how = 'left')
    merge = merge.rename(columns = {'code_x':'code_reg', 'code_y':'code_dep',
    'name_x':'name_reg',
    'name_y':'name_dep'})
    merge = merge.drop(columns = {'id_x','id_y','slug_x','slug_y','region_code'})
    return pd.DataFrame(merge)


def merge_referendum_and_areas(referendum, regions_and_departments):
    """Merge referendum and regions_and_departments in one DataFrame.

    You can drop the lines relative to DOM-TOM-COM departments, and the
    french living abroad, which all have a code that contains `Z`.

    DOM-TOM-COM departments are departements that are remote from metropolitan
    France, like Guadaloupe, Reunion, or Tahiti.
    """
    # Convert Department code to zero-padded format to match code_dep
    referendum["Department code"] =\
          referendum["Department code"].astype(str).str.zfill(2)

    # Now merge on the codes (more reliable than names)
    df = referendum.merge(regions_and_departments,
                        left_on="Department code",
                        right_on="code_dep",
                        how="left")

    df.drop_duplicates(inplace=True)
    df = df[~df["code_dep"].str.contains("Z", na=False)]
    df.dropna(inplace=True)
    return df




def compute_referendum_result_by_regions(referendum_and_areas):
    """Return a table with the absolute count for each region.

    The return DataFrame should be indexed by `code_reg` and have columns:
    ['name_reg', 'Registered', 'Abstentions', 'Null', 'Choice A', 'Choice B']
    """
    df_results = referendum_and_areas.groupby('code_reg', as_index=True).agg({
        'name_reg': 'first',
        'Registered': 'sum',
        'Abstentions': 'sum',
        'Null': 'sum',
        'Choice A': 'sum',
        'Choice B': 'sum'
    })
    df_results = df_results[['name_reg', 'Registered', 'Abstentions',
                             'Null', 'Choice A', 'Choice B']]
    return df_results


def plot_referendum_map(referendum_result_by_regions):
    """Plot a map with the results from the referendum.

    * Load the geographic data with geopandas from `regions.geojson`.
    * Merge these info into `referendum_result_by_regions`.
    * Use the method `GeoDataFrame.plot` to display the result map. The results
      should display the rate of 'Choice A' over all expressed ballots.
    * Return a gpd.GeoDataFrame with a column 'ratio' containing the results.
    """

    gdf = gpd.read_file("data/regions.geojson")

    # Reset index to make code_reg a column for merging
    referendum_df = referendum_result_by_regions.reset_index()

    # Merge on the region code
    merged_gdp = gdf.merge(referendum_df,
                           left_on="code",
                           right_on="code_reg")

    # Convert to GeoDataFrame
    merged_gdp = gpd.GeoDataFrame(merged_gdp, geometry="geometry")

    # Calculate ratio: Choice A / expressed ballots
    expressed_ballots = merged_gdp["Choice A"] + merged_gdp["Choice B"]
    merged_gdp["ratio"] = merged_gdp["Choice A"] / expressed_ballots

    # Plot the map
    merged_gdp.plot(column="ratio", legend=True)

    return merged_gdp


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
