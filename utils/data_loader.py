from pathlib import Path
import geopandas as gpd
import streamlit as st
import pandas as pd

@st.cache_data
def load_all_data():

    GPKG_PATH_NUTS3 = Path("data") / "weighted_aggr_nuts_3.gpkg"
    GPKG_PATH_NUTS2 = Path("data") / "weighted_aggr_nuts_2.gpkg"
    GPKG_PATH_NUTS1 = Path("data") / "weighted_aggr_nuts_1.gpkg"

    gdf_nuts3 = gpd.read_file(GPKG_PATH_NUTS3).to_crs(epsg=4326)
    gdf_nuts2 = gpd.read_file(GPKG_PATH_NUTS2).to_crs(epsg=4326)
    gdf_nuts1 = gpd.read_file(GPKG_PATH_NUTS1).to_crs(epsg=4326)

    # simplify the geometries for faster rendering
    gdf_nuts3['geometry'] = gdf_nuts3['geometry'].simplify(tolerance=0.01)
    gdf_nuts2['geometry'] = gdf_nuts2['geometry'].simplify(tolerance=0.01)
    gdf_nuts1['geometry'] = gdf_nuts1['geometry'].simplify(tolerance=0.01)
    
    preview_nuts3 = gdf_nuts3.drop(columns=["geometry", "CENTER_X", "CENTER_Y", "CENTER_LAT", "CENTER_LON"],
                                    errors="ignore").head(6)
    
    gdf_nuts3 = gdf_nuts3.__geo_interface__
    gdf_nuts2 = gdf_nuts2.__geo_interface__
    gdf_nuts1 = gdf_nuts1.__geo_interface__

    return {
        "NUTS3": gdf_nuts3,
        "NUTS2": gdf_nuts2,
        "NUTS1": gdf_nuts1,
        "PREVIEW_NUTS3": preview_nuts3
    }


@st.cache_data
def load_model_predictions(id = 1):
    GPKG_PATH = Path("data/predictions") / f"{id}_MODEL_PREDICTIONS.gpkg"

    gdf_model = gpd.read_file(GPKG_PATH).to_crs(epsg=4326)
    gdf_model['geometry'] = gdf_model['geometry'].simplify(tolerance=0.01)
    min_val = gdf_model['y_pred'].min()
    max_val = gdf_model['y_pred'].max()

    gdf = gdf_model.__geo_interface__

    return (gdf, min_val, max_val)

@st.cache_data
def load_data_coverage_image():
    IMAGE_PATH = Path("data/images") / "data_coverage.svg"
    with open(IMAGE_PATH, "r", encoding="utf-8") as f:
        return f.read()
    
def load_model_results():
    CSV_PATH = Path("data") / "MODELS.csv"
    df = pd.read_csv(CSV_PATH, sep=";")
    return df


