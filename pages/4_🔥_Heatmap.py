import streamlit as st
import leafmap.foliumap as leafmap
import pandas as pd

# Set the page layout to wide
st.set_page_config(layout="wide")

# Title of the app
st.title("Heatmap of Indian Cities")

# Load the dataset from the local folder
# file_path = "../data/GlobalLandTemperaturesByCity.csv"  # this file is too large if u want to still want contact me!!
try:
    data = pd.read_csv(file_path)
    st.write("Dataset Preview:")
    st.write(data.head())
except FileNotFoundError:
    st.error(f"File not found: {file_path}")

# Initialize the map centered on India
m = leafmap.Map(center=[20.5937, 78.9629], zoom=5)

# Add heatmap layer
m.add_heatmap(
    data,
    latitude="latitude",
    longitude="longitude",
    value="value",  # Change this to the actual column name for values in your dataset
    name="Heatmap of Indian Cities",
    radius=20
)

# Render the map in the Streamlit app
m.to_streamlit(height=700)
