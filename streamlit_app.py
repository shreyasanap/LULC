import streamlit as st
import leafmap.foliumap as leafmap

st.set_page_config(layout="wide")

st.title("Streamlit for Geospatial Applications")

row1_col1, row1_col2 = st.columns(2)
with row1_col1:
    st.image("Navi Mumbai Airport.gif")
    st.image("https://github.com/giswqs/data/raw/main/timelapse/las_vegas.gif")

with row1_col2:
    st.image("https://github.com/giswqs/data/raw/main/timelapse/goes.gif")
    st.image("https://github.com/giswqs/data/raw/main/timelapse/fire.gif")

