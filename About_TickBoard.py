import streamlit as st
from pathlib import Path
import pandas as pd
import geopandas as gpd
from utils.data_loader import load_all_data

st.set_page_config(
    page_title="TickBoard",
    page_icon="🕷️",
    layout="wide"
)

st.title("🕷️ TickBoard: Predictive Analysis of Tick Abundance in Europe")
st.divider()

col1, col2 = st.columns([1.1, 1], gap = "large",  vertical_alignment="top")
if 'center_lat' not in st.session_state:
    st.session_state['center_lat'] = 48.3
if 'center_lon' not in st.session_state:
    st.session_state['center_lon'] = 11.2
if 'current_nuts_level' not in st.session_state:
    st.session_state['current_nuts_level'] = 'NUTS3'

with col1:
    st.markdown("### A Data-Driven Approach to Understanding Tick Distribution")

    st.markdown("""
    **Authors:**  
    - Barbara Seweryn
    - Michał Wietecki  
    
    **Supervisor**: dr Katarzyna Woźnica
    
    **Institution**: Faculty of Mathematics and Information Science, Warsaw University of Technology
    """)

    st.divider()
    st.markdown("#### Problem outline")
    st.markdown("""
    Tick-borne diseases are a growing problem in healthcare in Europe. 
    Effective monitoring and prediction of tick occurrences are crucial for public health, planning preventive measures, and minimizing the risk of human exposure to pathogens transmitted by these parasites.
    
    This topic was brought to our attention by grant OneTick leaded by professor Michał Burdukiewicz
    of **Medical University of Białystok**. Białystok is the capital of Podlaskie Voivodeship, which is one of
    the **most endangered regions** in Poland when it comes to tick-borne diseases, because of high forestation and many crucial jobs and activities connected to spending time in the forest. **Lyme disease** and
    **Tick-borne encephalitis** are one of the most dangerous threats to the people living in that region.
    
    **Lyme disease** is a bacterial disease caused by Borrelia bacteria, transmitted to humans and
    some animals by ticks of the Ixodes genus. The first symptom of this disease is erythema migrans,
    an oval-shaped reddening of the skin with the tick bite in the center. If left untreated, it can
    lead to permanent damage to the joints, nervous system, and heart. 
    
    **Tick-borne encephalitis (TBE)** is a viral disease of the central nervous system, also transmitted by
    ticks. Because it is a viral disease, the vaccine is available however it requires three initial doses
    and a reminding dose every 3-5 years. Each dose in Europe costs approximately 30-90 euros therefore the
    percentage of vaccinated population is extremely low. Initial symptoms include weakness and
    fever, followed by severe headaches, neck stiffness, and impaired consciousness. It can cause
    permanent neurological complications (e.g., paralysis, memory problems).
    """)

with col2:
    st.markdown("#### Our goals")
    st.markdown("""
    The **TickBoard** project aims to provide an interactive, data-driven platform for exploring **tick abundance**, **environmental predictors**, and **spatial-temporal patterns** based on official data from the **European Centre for Disease Prevention and Control (ECDC)** and other environmental sources.
    
    Our goal is to:
    - Integrate environmental and tick monitoring data at the **NUTS1**, **NUTS2**, **NUTS3** regional level,  
    - Apply **classic and spatial predictive ML models** to estimate tick abundance i Europe, 
    - Visualize the results using an intuitive **Streamlit interface** to assist users in assessment
    of the risk of getting a tick bite in a specific region of Europe and the urgency of applying
    preventative actions.
    """)

    st.divider()
    st.markdown("#### Future benefits")
    st.markdown("""
    Future benefits of TickBoard include:
    - **Awareness** - people being more aware of the risks of tick-borne diseases in the region they live or are planning on travelling to
    - **Resource allocation** - public and private health care resources allocation to prevent and treat tick-borne diseases, decreasing the risk of temporal shortages of resources in case of sudden outbreaks, which are more likely to occur in regionswith higher tick populations.
    - **Education** - serving public institutions such as national or local governments, including their educational branches, by supporting the introduction of awareness campaigns addressing the issue
    """)

st.markdown("""
---
© TickBoard | Developed in Python using [Streamlit](https://streamlit.io/)
""")

if "nuts_geojson_data" not in st.session_state:
    st.session_state["nuts_geojson_data"] = load_all_data()