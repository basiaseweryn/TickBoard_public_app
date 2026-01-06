import streamlit as st
import pandas as pd
from utils.data_upload_validation import validate_env_data
from utils.data_loader import load_all_data

st.set_page_config(
    page_title="Upload New Data | TickBoard",
    page_icon="🕷️",
    layout="wide")


#image_path = os.path.join(os.path.dirname(__file__), "..", "TickBoard.png")
#st.logo(Image.open(image_path), size = "large")

st.title("Upload New Environmental Data ")
st.subheader("Help us develop our experiments and explore the tick habitat suitability topic further!")

st.divider()

col1, col2 = st.columns([1.3, 1], gap = "large")

with col1:
    st.markdown("#### Environmental Data Upload")
    st.markdown("""
    For your .csv (semicolon separated) file to successfully undergo validation and the variable to be added to the dataset:
    - the file has to contain two columns (NUTS3 code + variable value) and no headers,
    - all variable values have to be numerical,
    - no NUTS3 code can appear more than once in the file,
    - the variable name the user declared in the textbox in the dashboard is not the same as any of the variables already included in the environmental dataset.
    - the file has to contain values for each European NUTS3 code.
                """)

    variable_name = st.text_input("Write the name of the variable here")
    env_file = st.file_uploader(label = "Environmental data file", type = "csv",
                     accept_multiple_files = False, key = "env_data_uploader",
                     help = "Input your file with new environmental variables here")
    if col1.button("Upload Environmental Data"):
        if env_file is not None:
            env_df = pd.read_csv(env_file, header=None, sep = ";")
            passed, message = validate_env_data(env_df, variable_name) #passed = T => the file has passed all validation steps
            if passed:
                st.success("Thank you for uploading your environmental data and improving our database!", icon="✅")
            else:
                st.error(message, icon="🚨")


with col2:
    st.markdown("#### Sample of the current environmental dataset")

    if "nuts_geojson_data" not in st.session_state:
        with st.spinner("Data is still loading..."):
            st.session_state["nuts_geojson_data"] = load_all_data()

    st.dataframe(st.session_state["nuts_geojson_data"]["PREVIEW_NUTS3"])



st.markdown("""
---
© TickBoard | Developed in Python using [Streamlit](https://streamlit.io/)
""")