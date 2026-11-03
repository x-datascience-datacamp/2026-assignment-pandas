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
    referendum = pd.read_csv("./data/referendum.csv", sep=";")
    regions = pd.read_csv("./data/regions.csv")
    departments = pd.read_csv("./data/departments.csv")

    return referendum, regions, departments


def merge_regions_and_departments(regions, departments):
    """Merge regions and departments in one DataFrame.

    The columns in the final DataFrame should be:
    ['code_reg', 'name_reg', 'code_dep', 'name_dep']
    """
    reg=regions.rename(
        columns={"code":"code_reg","name":"name_reg"}
    )
    dep=departments.rename(
        columns={"code":"code_dep","name":"name_dep"}
    )

    res=pd.merge(reg,dep, how="inner", left_on="code_reg",right_on="region_code")

    return res[['code_reg', 'name_reg', 'code_dep', 'name_dep']]


def merge_referendum_and_areas(referendum, regions_and_departments):
    """Merge referendum and regions_and_departments in one DataFrame.

    You can drop the lines relative to DOM-TOM-COM departments, and the
    french living abroad, which all have a code that contains `Z`.

    DOM-TOM-COM departments are departements that are remote from metropolitan
    France, like Guadaloupe, Reunion, or Tahiti.
    """
    ref=referendum.copy()
    reg_dep=regions_and_departments.copy()
    ref_dep=ref["Department code"]
    ref["Department code"] = ref_dep.astype(str).str.zfill(2)
    reg_dep_c=reg_dep["code_dep"]
    reg_dep["code_dep"] = reg_dep_c.astype(str).str.zfill(2)
    df=pd.merge(ref,reg_dep, how="left", left_on="Department code", right_on="code_dep")
    mask_z = df["Department code"].str.contains("Z")
    df = df[~mask_z].dropna()

    return df


def compute_referendum_result_by_regions(referendum_and_areas):
    """Return a table with the absolute count for each region.

    The return DataFrame should be indexed by `code_reg` and have columns:
    ['name_reg', 'Registered', 'Abstentions', 'Null', 'Choice A', 'Choice B']
    """
    count_cols = ["Registered", "Abstentions", "Null", "Choice A", "Choice B"]

    # Agrégation : 'first' pour conserver le nom de région, 'sum' pour les effectifs
    agg_dict = {col: "sum" for col in count_cols}
    agg_dict["name_reg"] = "first"

    df = (
        referendum_and_areas.groupby("code_reg")
        .agg(agg_dict)
    )

    cols_order = ["name_reg"]+count_cols

    return df[cols_order]

def plot_referendum_map(referendum_result_by_regions):
    """Plot a map with the results from the referendum.

    * Load the geographic data with geopandas from `regions.geojson`.
    * Merge these info into `referendum_result_by_regions`.
    * Use the method `GeoDataFrame.plot` to display the result map. The results
      should display the rate of 'Choice A' over all expressed ballots.
    * Return a gpd.GeoDataFrame with a column 'ratio' containing the results.
    """
    geo_df = gpd.read_file("./data/regions.geojson")
    # Ratio de 'Choice A' sur l'ensemble des suffrages exprimés (Choice A + Choice B)
    df = referendum_result_by_regions.copy()
    expressed_votes = df["Choice A"] + df["Choice B"]
    df["ratio"] = df["Choice A"] / expressed_votes

    # Clé de code de région dans le GeoJSON (souvent 'code' ou 'code_reg')
    geo_key = "code_reg" if "code_reg" in geo_df.columns else "code"
    geo_df[geo_key] = geo_df[geo_key].astype(str)
    df.index = df.index.astype(str)

    # Fusion avec les polygones
    merged_gdf = geo_df.merge(df, left_on=geo_key, right_index=True)
    merged_gdf = gpd.GeoDataFrame(merged_gdf, geometry="geometry")

    # Tracé de la carte
    fig, ax = plt.subplots(figsize=(12, 10))
    merged_gdf.plot(
        column="ratio",
        cmap="coolwarm",
        legend=True,
        legend_kwds={"label": "Rate of Choice A over expressed ballots"},
        ax=ax,
    )
    ax.set_axis_off()

    return merged_gdf



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
