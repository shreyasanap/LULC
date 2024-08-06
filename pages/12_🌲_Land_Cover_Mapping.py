import datetime
import ee
import streamlit as st
import geemap.foliumap as geemap

# Set Streamlit page configuration at the start
st.set_page_config(layout="wide")

# Initialize Earth Engine
def initialize_earth_engine():
    try:
        ee.Initialize(project='ee-shreya20comp')
        st.write("Earth Engine initialized successfully.")
    except Exception as e:
        st.error(f"Error initializing Earth Engine: {e}")

# Call the initialization function
initialize_earth_engine()

st.title("Comparing Global Land Cover Maps")

col1, col2 = st.columns([4, 1])

# Create the map instance with default options
Map = geemap.Map()

# Add default basemaps
Map.add_basemap("HYBRID")  # Using a known available basemap for testing

# Define visualizations
esa_vis = {"bands": ["Map"]}
esri_vis = {
    "min": 1,
    "max": 10,
    "palette": [
        "#1A5BAB",
        "#358221",
        "#A7D282",
        "#87D19E",
        "#FFDB5C",
        "#EECFA8",
        "#ED022A",
        "#EDE9E4",
        "#F2FAFF",
        "#C8C8C8",
    ],
}

markdown = """
    - [Dynamic World Land Cover](https://developers.google.com/earth-engine/datasets/catalog/GOOGLE_DYNAMICWORLD_V1?hl=en)
    - [ESA Global Land Cover](https://developers.google.com/earth-engine/datasets/catalog/ESA_WorldCover_v100)
    - [ESRI Global Land Cover](https://samapriya.github.io/awesome-gee-community-datasets/projects/esrilc2020)
"""

with col2:
    longitude = st.number_input("Longitude", -180.0, 180.0, -89.3998)
    latitude = st.number_input("Latitude", -90.0, 90.0, 43.0886)
    zoom = st.number_input("Zoom", 0, 20, 11)

    Map.setCenter(longitude, latitude, zoom)

    start = st.date_input("Start Date for Dynamic World", datetime.date(2020, 1, 1))
    end = st.date_input("End Date for Dynamic World", datetime.date(2021, 1, 1))

    start_date = start.strftime("%Y-%m-%d")
    end_date = end.strftime("%Y-%m-%d")

    region = ee.Geometry.BBox(-179, -89, 179, 89)

    try:
        dw = geemap.dynamic_world(region, start_date, end_date, return_type="hillshade")
        dw_layer = geemap.ee_tile_layer(dw, {}, "Dynamic World Land Cover")
    except Exception as e:
        st.error(f"Error retrieving Dynamic World data: {e}")
        dw_layer = None

    esa = ee.ImageCollection("ESA/WorldCover/v100").first()
    esri = ee.ImageCollection(
        "projects/sat-io/open-datasets/landcover/ESRI_Global-LULC_10m"
    ).mosaic()

    layers = {}
    if dw_layer:
        layers["Dynamic World"] = dw_layer
    if esa:
        layers["ESA Land Cover"] = geemap.ee_tile_layer(esa, esa_vis, "ESA Land Cover")
    if esri:
        layers["ESRI Land Cover"] = geemap.ee_tile_layer(esri, esri_vis, "ESRI Land Cover")

    options = list(layers.keys())
    left = st.selectbox("Select a left layer", options, index=1 if len(options) > 1 else 0)
    right = st.selectbox("Select a right layer", options, index=0)

    left_layer = layers.get(left, None)
    right_layer = layers.get(right, None)

    if left_layer and right_layer:
        try:
            Map.split_map(left_layer, right_layer)
        except ValueError as e:
            st.error(f"Error with split_map: {e}")

    legend = st.selectbox("Select a legend", options, index=options.index(right) if options else 0)
    if legend == "Dynamic World" and dw_layer:
        Map.add_legend(
            title="Dynamic World Land Cover",
            builtin_legend="Dynamic_World",
        )
    elif legend == "ESA Land Cover" and esa:
        Map.add_legend(title="ESA Land Cover", builtin_legend="ESA_WorldCover")
    elif legend == "ESRI Land Cover" and esri:
        Map.add_legend(title="ESRI Land Cover", builtin_legend="ESRI_LandCover")

    with st.expander("Data sources"):
        st.markdown(markdown)

with col1:
    Map.to_streamlit(height=750)