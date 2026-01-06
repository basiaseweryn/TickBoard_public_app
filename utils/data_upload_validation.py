import pandas as pd
from collections import Counter
import geopandas as gpd
import csv
from pathlib import Path

#table paths
env_versions = Path("data") / "ENV_VARIABLES_VERSIONS.csv"
country_versions = Path("data") / "COUNTRY_VERSIONS.csv"
tick_data = Path("data") / "TICKS.csv"
env_data = Path("data") / "weighted_aggr_nuts_3.gpkg"
nuts_country_codes = Path("data") / "NUTS_COUNTRY_CODES.csv" #two first characters of nuts codes for each country


def validate_env_data(df, variable_name):
    if not isinstance(df, pd.DataFrame):
        return False, "This data is in the wrong format."
    if df.empty:
        return False, "This data is empty."
    if len(df.columns) !=2:
        return False, "The file has to contain exactly two columns."

    df.columns = ["RegionCode", variable_name]
    uploaded_nuts = list(df["RegionCode"])

    #checking if a variable with the same name already exists
    env_df = gpd.read_file(env_data)
    env_variables = env_df.columns
    if df.columns[1] in env_variables:
        return False, "The environmental data already contains a variable with this name."

    #checking for non-numerical values
    if not all(isinstance(x, (int, float)) for x in df[df.columns[1]]):
        return False, "This data contains non-numerical values."

    # checking for duplicates
    duplicated_nuts = [x for x, count in Counter(uploaded_nuts).items() if count > 1]
    if len(duplicated_nuts) > 0:
        return False, "This data contains more than one value for the following regions: " + str(duplicated_nuts)

    #checking if file has too many nuts
    nuts3 = list(env_df["NUTS_ID"])  # list of all NUTS3 codes in our data
    if len(set(uploaded_nuts)) > len(set(nuts3)):
        fake_nuts = set(uploaded_nuts) - set(nuts3)
        return False, "This data contains these fake NUTS3 codes:" + str(fake_nuts)

    #checking if any nuts are missing
    if set(uploaded_nuts) != set(nuts3):
        missing_nuts = set(nuts3) - set(uploaded_nuts)
        return False, "This data lacks values for " + str(missing_nuts)

    #add function adding this data to the database
    env_version_table = pd.read_csv(env_versions, sep=";")
    env_version_table_max_version = env_version_table["version"].max()
    if add_env_data(df, env_version_table_max_version, variable_name):
        return True, "The data has been uploaded successfully."
    else:
        return False, "Something went wrong during adding the uploaded data to our dataset. Please try again."

def add_env_data(df, version, variable_name):
    version+=1
    try:
        #update env_variables_version table by adding the name of the new variable and inserting version value one bigger than the latest
        with open(env_versions, "a", newline="", encoding="utf-8") as f:
            writer = csv.writer(f, delimiter=";")
            writer.writerow([df.columns[1], version])
        # add the new variable as a new column in the environmental dataset
        gdf_nuts3 = gpd.read_file(env_data).to_crs(epsg=4326)
        # print(gdf_nuts3.columns)
        df.columns = ["NUTS_ID", variable_name]
        # print(df.columns)
        gdf_nuts3_merged = gdf_nuts3.merge(df, on="NUTS_ID", how="left")
        # print(gdf_nuts3_merged.columns)
        gdf_nuts3_merged.to_file(env_data, driver="GPKG")
        return True
    except FileNotFoundError:
        return False
