import streamlit as st
import pandas as pd
import importlib
import pydeck as pdk
import time
import utils.data_loader as data_loader
importlib.reload(data_loader)
st.cache_data.clear()


st.set_page_config(
    page_title="Tick Abundance Prediction | TickBoard",
    page_icon="🕷️",
    layout="wide"
)

if 'selected_second_id' not in st.session_state:
    st.session_state['selected_second_id'] = 2
if 'is_training' not in st.session_state:
    st.session_state['is_training'] = False


st.title("Tick Abundance Prediction")
st.divider()

def get_available_models():
    try:
        df = pd.read_csv("data/MODELS.csv", sep=";")
        df = df.iloc[1:] # exclude the main model with id 1
        return list(zip(df['model_id'], df['model_name'], df['creation_date']))
    except (FileNotFoundError, pd.errors.EmptyDataError):
        return []

def map_model_predictions(id='main', title=""):
    target_id = 1 if id == 'main' else id
    
    with st.spinner(f"Loading predictions..."):
        gdf, min_v, max_v = data_loader.load_model_predictions(id=target_id)
        denom = (max_v - min_v) if max_v != min_v else 1
        
        layer = pdk.Layer(
            "GeoJsonLayer",
            data=gdf,
            get_fill_color=f"""
            [
                128 + ( (properties.y_pred - {min_v}) / {denom} * 127 ), 
                0 + ( (properties.y_pred - {min_v}) / {denom} * 255 ), 
                128 - ( (properties.y_pred - {min_v}) / {denom} * 128 ), 
                160
            ]
            """,
            get_line_color=[0, 20, 0],
            line_width_min_pixels=1,
            pickable=True,
        )

        st.pydeck_chart(
            pdk.Deck(
                map_style="mapbox://styles/mapbox/light-v10",
                initial_view_state=pdk.ViewState(
                    latitude=48.3, longitude=11.2, zoom=3.5
                ),
                layers=[layer],
                tooltip={"html": "<b>Value:</b> {y_pred}"}
            )
        )

@st.fragment
def training_section():
    if st.button("Train model",width="stretch", disabled=True,
                     help="This functionality is not available in the public version of TickBoard dashboard, since training data is confidential"):
        with st.spinner("Training in progress..."):
            #model_training.train_model()
            st.cache_data.clear()
        st.success("Trained!")
        st.rerun()

col1, col2 = st.columns([1, 1])

with col1:
    st.markdown("#### Main model predictions")
    st.markdown("##### Spatiotemporal Random Forest, ID = 1")
    st.markdown("Model specification described below the maps")
with col2:
    st.markdown("#### Comparison model predictions")
    
    ctrl_col1, ctrl_col2 = st.columns([1, 2])
    
    with ctrl_col1:
        training_section()

    with ctrl_col2:
        models_options = get_available_models()
        
        current_id = st.session_state['selected_second_id']
        try:
            idx = [m[0] for m in models_options].index(current_id)
        except (ValueError, IndexError):
            idx = 0

        selected_tuple = st.selectbox(
            label = "Select model to compare",
            label_visibility="collapsed",
            help="Select a model to compare with the main model",
            options=models_options,
            index=idx,
            format_func=lambda x: f"{x[0]} - {x[1]}" if int(x[0]) <= 4 else f"{x[0]} - {x[1]} (created: {x[2]})",
            key="model_selector_widget",
            width="stretch"
        )
        
        if selected_tuple:
            st.session_state['selected_second_id'] = int(selected_tuple[0])

col1, col2 = st.columns([1, 1])
with col1:
    map_model_predictions(id='main')
with col2:
    map_model_predictions(id=st.session_state['selected_second_id'])

st.divider()
col1, col_divider, col2 = st.columns([1, 0.1, 1])
with col1:
    st.markdown("## Methodology")
    st.markdown("### Machine learning algorithms")
    st.markdown("""The primary objective of this project was to evaluate the performance of spatially explicit models on
                tick population abundance predictions compared to classic machine learning frameworks. Secondarily, the research was meant to prove the
                non-linear relationships existing between environmental attributes and tick population. To achieve 
                these goals, we tested and compared four distinct machine learning models:
* **Linear Regression** - a baseline statistical model, that assumes a linear relationship between attributes and the
                target variable.
* **Random Forest** - an ensemble machine learning method used to capture non-linearities by combining multiple decision
                trees’ predictions.
* **Geographically Weighted Regression** - a localized form of linear regression that allows relationships between
                variables to vary across geographical space.
* **Spatiotemporal Random Forest** - a spatial enhancement of the global Random Forest algorithm, with an additional system of
                weighted bootstraping of neighboring observations.""")
    st.markdown("### Model optimization and evaluation")
    st.markdown("""During the modeling phase, the optimization goal was to minimize the **Mean Absolute Error** ($MAE$). It
                is resilient to outliers, which were likely to occur outside of typical tick outburst areas in 
                our dataset (as explained on the [data overview page](/Data_overview#ecdc-tick-abundance-data)). MAE helped us to 
                assess models’ ability of predicting typical density
                of tick population across Europe. However, to ensure the reliability of the models, we concurrently
                monitored the Coefficient of Determination ($R^2$, a model with an $R^2$ of zero or less performs no better than a baseline model that
                constantly predicts the mean value of the dataset). This dual-metric approach was adopted to prevent
                selecting a model that achieves a low MAE by chance without explaining any actual variance in the data.
                For each modeling framework, a single set of optimal
                hyperparameters was selected based on their predictive performance during gri search experiments.<br><br>All models were evaluated using Leave-One-Out Cross-Validation (LOOCV). In this method, a prediction
                for a single set of environmental variables is made by using all other available data points.""", unsafe_allow_html=True)
    st.markdown("### Data tranformation")
    st.markdown("""To address the skewness in tick abundance data and better satisfy the assumptions of linear models, 
                specific variables (including the tick abundance) were transformed using logarithmic scaling before 
                modeling (only the linear models), followed by standardization. To ensure fair comparability between models, retrieved predictions
                were then transformed back to the original scale. This allowed for consistent calculation of error metrics.""")

with col_divider:
    pass
with col2:
    st.markdown("## Results")
    st.dataframe(data_loader.load_model_results(), hide_index=True, column_order = ['model_id', 'model_name', 'creation_date', 'mae', 'rmse', 'r2', 'mean_true', 'mean_pred', 'std_true', 'std_pred', 'parameters', 'env_data_version'])
    st.markdown("### Model Performance Analysis")
    st.markdown("""Based on the perfomnace metrics presented above, to conclusions can be drawn:
* **Non-linearity**: both linear models were significantly outperformed by the tree-based models. Their 
                $R^2$ values were less than 0, which indicates that they failed to explain any variance hidden in the data.
                This makes it clear that the relationship between environmental factors and tick abundance is non-linear.
* **Spatial component**: the spatial enhancement of STRF model proved to be beneficial as it's average results 
                were a little bit better than those of a standard global RF. 
* **Target data compleixity**: the relatively high MAE values across all models prove that the target dataset's
                flaws make the prediction task very challenging.""")
                
st.markdown("""
---
© TickBoard | Developed in Python using [Streamlit](https://streamlit.io/)
""")