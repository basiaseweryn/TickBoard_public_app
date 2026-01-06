import streamlit as st
import pydeck as pdk
import time
import importlib
import utils.data_loader as data_loader
importlib.reload(data_loader)
from branca.colormap import linear
from utils.data_loader import load_all_data

st.set_page_config(
    page_title="Data Overview | TickBoard",
    page_icon="🕷️",
    layout="wide")

st.title("🌍 Data Overview")
st.divider()

col1, col2 = st.columns([1, 1.2])


with col1:
    st.markdown("#### Environmental data description")

    st.markdown("""
    The collected data was a GIS dataset (GeoPackage format) of hexagonal grids over Europe,
    with data on **climate, landscape and vegetation** features.
    This data consisted of **hexagonal cells** covering the continent of Europe, each of which had a **diameter of
    20 km** (or less in case of land-sea borders). Since the **NUTS** (Nomenclature of Territorial Units) European area division standard is the one on which most EU-wide statistics are performed, including the 
    ECDC (European Centre for Disease Control and Prevention) tick abundance data, we have mapped the hexagonal environmental data onto the NUTS format.
    The final environmental dataset used in the TickBoard project along with its environmental variables is displayed on the right side of this page.
    """)

    st.divider()
    st.markdown("#### Environmental variables")
    st.markdown("""
    - EEAmedian = Median value of the vegetation category (the most represented value in the target cell),
    - EEAminorit = The category of vegetation of the largest patch in the target cell,
    - EEAmajorit = The category of vegetation of the smallest patch in the target cell,
    - EEAvariety = The number of different categories of vegetation in the target cell of the grid,
    - TCDmedian, TCDvarianc, TCDsum = median, variance and sum of the tree coverage in the area(s) of forest,
    - TCDcount = Area of forest,
    - TMAX1, TMAX2, TMAX3 = First, second and third coefficient of the harmonic regression of the maximum temperature (1990–2020), first being the mean,
    - TMIN1, TMIN2, TMIN3 = First, second and third coefficient of the harmonic regression of the minimum temperature (1990–2020), first being the mean,
    - VPD1, VPD2, VPD3 = First, second and third coefficient of the harmonic regression of the water vapour deficit (1990–2020), first being the mean,
    - BufferFTY = Average distance of all the pixels in a cell to the nearest forest patch,
    - BufferGras = Average distance of all the pixels in a cell to the nearest patch of grass,
    - BufferImpe = The average distance between impervious surface and any other vegetated patch in the target cell,
    - Impervious = Impervious surface in the target cell.
    """)

with col2:
    start = time.time()
    if "nuts_geojson_data" not in st.session_state:
        st.session_state["nuts_geojson_data"] = load_all_data()
    if 'nuts_layers' not in st.session_state:
        layer_NUTS3 = pdk.Layer(
            "GeoJsonLayer",
            data=st.session_state["nuts_geojson_data"]["NUTS3"]["features"],
            get_polygon="geometry.coordinates[0]",
            get_fill_color="properties['VALUE']",
            get_line_color=[250,240,230],
            line_width_min_pixels=0.5,
            pickable=True,
        )

        layer_NUTS2 = pdk.Layer(
            "GeoJsonLayer",
            data=st.session_state["nuts_geojson_data"]["NUTS2"]["features"],
            get_polygon="geometry.coordinates[0]",
            get_fill_color="properties['VALUE']",
            get_line_color=[250,240,230],
            line_width_min_pixels=1,
            pickable=True,
        )

        layer_NUTS1 = pdk.Layer(
            "GeoJsonLayer",
            data=st.session_state["nuts_geojson_data"]["NUTS1"]["features"],
            get_polygon="geometry.coordinates[0]",
            get_fill_color="properties['VALUE']",
            get_line_color=[250,240,230],
            line_width_min_pixels=1,
            pickable=True,
        )

        st.session_state['nuts_layers'] = {
            'NUTS3': layer_NUTS3,
            'NUTS2': layer_NUTS2,
            'NUTS1': layer_NUTS1,
        }
    end = time.time()
    print(f"All layers created in {end - start:.2f}s")

    def change_active_map():
        st.rerun()
    sub_col_1, sub_col_2 = st.columns([1, 1.8])
    with sub_col_1:
        st.pills("Select NUTS level:", ["NUTS3", "NUTS2", "NUTS1"], selection_mode="single", default ="NUTS3",
                        key = "active_nuts_level")
    with sub_col_2:
        st.selectbox("Select environmental variable", ["EEAmedian","EEAminorit", "EEAmajorit","EEAvariety","TCDmedian","TCDvarianc","TMAX1","TMAX2","TMAX3","TMIN1","TMIN2","TMIN3","VPD1","VPD2","VPD3","BufferFTY","BufferGras", "BufferImpe","TCDcount","TCDsum","Impervious"],
                 key = "current_environmental_variable")
    if "last_env_var" not in st.session_state:
        st.session_state["last_env_var"] = None
    if "last_nuts_level" not in st.session_state:
        st.session_state["last_nuts_level"] = None

    if st.session_state["last_env_var"] != st.session_state["current_environmental_variable"] or \
            st.session_state["last_nuts_level"] != st.session_state["active_nuts_level"]:
        st.session_state["last_env_var"] = st.session_state["current_environmental_variable"]
        st.session_state["last_nuts_level"] = st.session_state["active_nuts_level"]
        st.rerun()
    with st.spinner("Generating the map..."):
        start = time.time()
        var = st.session_state["current_environmental_variable"]
        level = st.session_state["active_nuts_level"]
        features = st.session_state["nuts_geojson_data"][level]["features"]
        values = [f["properties"].get(var) for f in features if f["properties"].get(var) is not None]
        vmin, vmax = round(min(values),2), round(max(values),2)
        colormap = linear.viridis.scale(vmin, vmax)
        colormap.caption = var
        colormap.format = "{:.2f}"
        for f in features:
            val = f["properties"].get(var)
            if val is None:
                f["properties"]["VALUE"] = [180, 180, 180, 140]
            else:
                rgb = colormap(round(val,2)).lstrip("#")
                r, g, b = tuple(int(rgb[i:i + 2], 16) for i in (0, 2, 4))
                f["properties"]["VALUE"] = [r, g, b, 250]
        st.session_state["nuts_layers"][level].data = features

        first = features[0]["properties"]

        st.pydeck_chart(
            pdk.Deck(
                map_style="mapbox://styles/mapbox/light-v10",
                initial_view_state=pdk.ViewState(
                    latitude=48.3, longitude=11.2, zoom=3.5),
                layers=[st.session_state['nuts_layers'][level]],
                tooltip={"text": f"{var}: {{{var}}}\nNUTS_ID: {{NUTS_ID}}"}
            )
        )
        #st.markdown("##### Legend")
        sub_col1, sub_col2, sub_col3 = st.columns([0.5, 1.5, 0.5])
        with sub_col2:
            st.markdown(colormap._repr_html_(), unsafe_allow_html=True)
        end = time.time()
    print(f"Map rendered in {end - start:.2f}s")

    st.markdown("#### Sample of the Environmental Dataset")

    if "nuts_geojson_data" not in st.session_state:
        with st.spinner("Data is still loading..."):
            st.session_state["nuts_geojson_data"] = data_loader.load_all_data()

    st.dataframe(st.session_state["nuts_geojson_data"]["PREVIEW_NUTS3"])

st.divider()
sub_col1, sub_col2 = st.columns([1, 1.5])
with sub_col1:
    st.markdown("### ECDC Tick Abundance data")
    st.markdown("""
    The ECDC tick abundance data was build by gathering data from all official tick collection studies in Europe.
    Even though the dataset is official we still had a lot of difficulties with understanding and processing mostly because:
    - every study group collects and reports their data differently,
    - data is not collected uniformly in all regions, which reflects in the distribution. Some regions have a significantly larger tick abundance value, not necessarily because it features a more appealing habitat, but just because more extensive research has been conducted,
    - some regions have less funding for research, therefore the number of ticks found in those regions does not reflect the actual tick distribution.
    
    To make the dataset more reliable and suited for our problem we have:
    - filtered out data that did not have species specified as Ixodes Ricinius,
    - filtered out data that was lacking the information about the tick collection method used in the experiment,
    - handled outliers, ensuring no hyper-intensive studies can bias a specific region,
    - aggregated the data by region and year to receive a dataset representing the **average number of ticks found in each region per year**.
     
    The ECDC data is confidential, therefore we cannot provide a data exploration option for this dataset.
    However, what is much more important is the regional coverage this data provides, which is how many NUTS3 regions are included in the final dataset.
    This information can be seen on the map on the right side of this page. 
    """)
with sub_col2:
    sub_col1, sub_col2, sub_col3 = st.columns([0.2, 1.5, 0.5])
    with sub_col2:
        st.markdown("##### Final regional coverage of tick abundance dataset")
    st.image(data_loader.load_data_coverage_image(), width='stretch')

st.markdown("""
---
© TickBoard | Developed in Python using [Streamlit](https://streamlit.io/)
""")

