
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

    # Load all three CSV files.
    # Codes are strings because some start with zero or contain letters.
    referendum = pd.read_csv(
        "data/referendum.csv", sep=";",
        dtype={"Department code": str}
    )

    regions = pd.read_csv(
        "data/regions.csv",
        dtype={"code": str}
    )

    departments = pd.read_csv(
        "data/departments.csv",
        dtype={"code": str, "region_code": str}
    )

    return referendum, regions, departments


def merge_regions_and_departments(regions, departments):
    """Merge regions and departments in one DataFrame.

    The columns in the final DataFrame should be:
    ['code_reg', 'name_reg', 'code_dep', 'name_dep']
    """

    # Rename the columns so we can identify them easily.
    regions = regions.rename(columns={
        "code": "code_reg",
        "name": "name_reg"
    })

    departments = departments.rename(columns={
        "region_code": "code_reg",
        "code": "code_dep",
        "name": "name_dep"
    })

    # Merge using the region code.
    result = pd.merge(
        regions, departments, on="code_reg"
    )

    # Keep only the columns asked in the question.
    result = result[
        ["code_reg", "name_reg", "code_dep", "name_dep"]
    ]

    return result


def merge_referendum_and_areas(referendum, regions_and_departments):
    """Merge referendum and regions_and_departments in one DataFrame.

    You can drop the lines relative to DOM-TOM-COM departments, and the
    french living abroad, which all have a code that contains `Z`.

    DOM-TOM-COM departments are departements that are remote from metropolitan
    France, like Guadaloupe, Reunion, or Tahiti.
    """

    # Remove department codes containing Z.
    referendum = referendum[
        ~referendum["Department code"].str.contains("Z", na=False)
    ].copy()

    # Make sure department codes have the same format.
    referendum["Department code"] = (
        referendum["Department code"].str.zfill(2)
    )

    # Merge the voting results with region and department data.
    result = pd.merge(
        referendum,
        regions_and_departments,
        left_on="Department code",
        right_on="code_dep"
    )

    # Remove rows with missing values.
    result = result.dropna()

    return result


def compute_referendum_result_by_regions(referendum_and_areas):
    """Return a table with the absolute count for each region.

    The return DataFrame should be indexed by `code_reg` and have columns:
    ['name_reg', 'Registered', 'Abstentions', 'Null', 'Choice A', 'Choice B']
    """

    # Columns that contain the voting numbers.
    vote_columns = [
        "Registered",
        "Abstentions",
        "Null",
        "Choice A",
        "Choice B"
    ]

    # Add the voting numbers for each region.
    result = referendum_and_areas.groupby(
        ["code_reg", "name_reg"]
    )[vote_columns].sum()

    # Keep code_reg as the index and name_reg as a column.
    result = result.reset_index()
    result = result.set_index("code_reg")

    return result


def plot_referendum_map(referendum_result_by_regions):
    """Plot a map with the results from the referendum.

    * Load the geographic data with geopandas from `regions.geojson`.
    * Merge these info into `referendum_result_by_regions`.
    * Use the method `GeoDataFrame.plot` to display the result map. The results
      should display the rate of 'Choice A' over all expressed ballots.
    * Return a gpd.GeoDataFrame with a column 'ratio' containing the results.
    """

    # Load the geographical information.
    regions_map = gpd.read_file("data/regions.geojson")

    # Use the region code to match the two tables.
    regions_map = regions_map.rename(
        columns={"code": "code_reg"}
    )

    # Make sure both region codes are strings.
    regions_map["code_reg"] = regions_map["code_reg"].astype(str)

    # Merge the map with the referendum results.
    result = regions_map.merge(
        referendum_result_by_regions,
        left_on="code_reg",
        right_index=True
    )

    # Calculate the proportion of votes for Choice A.
    result["ratio"] = (
        result["Choice A"] /
        (result["Choice A"] + result["Choice B"])
    )

    # Plot the map.
    result.plot(
        column="ratio",
        cmap="Blues",
        legend=True
    )

    plt.title("Referendum Results by Region")

    return result


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
