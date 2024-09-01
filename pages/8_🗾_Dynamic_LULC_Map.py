import streamlit as st
import ee
import folium
import geemap.colormaps as cm
import geemap.foliumap as geemap
from streamlit_folium import folium_static

import ee

# Authenticate the Google Earth Engine account
ee.Authenticate()  

# Initialize the Earth Engine API with your specific project ID
ee.Initialize(project='lulc-429712')

# Streamlit app
st.title("Land Use Land Cover Map")

# User inputs for center coordinates and box size
st.sidebar.header("Input Coordinates for ROI")
center_lat = st.sidebar.number_input("Center Latitude", value=18.2335, format="%.2f")
center_lon = st.sidebar.number_input("Center Longitude", value=73.2626, format="%.2f")
box_size = st.sidebar.slider("Box Size (in degrees)", min_value=0.01, max_value=1.0, value=0.1)

# Calculate the bounding box coordinates
half_size = box_size / 2
ul_lat = center_lat + half_size  # Upper-left latitude
ul_lon = center_lon - half_size  # Upper-left longitude
lr_lat = center_lat - half_size  # Lower-right latitude
lr_lon = center_lon + half_size  # Lower-right longitude

# Define ROI using the bounding box
roi = ee.Geometry.Rectangle([ul_lon, lr_lat, lr_lon, ul_lat])

# Load Landsat 8 Collection 2 data and select relevant bands
image = ee.ImageCollection('LANDSAT/LC08/C02/T1_L2') \
    .filterBounds(roi) \
    .filterDate('2021-01-01', '2021-12-31') \
    .sort('CLOUD_COVER') \
    .first()

# Select bands for classification
bands = ['SR_B2', 'SR_B3', 'SR_B4', 'SR_B5', 'SR_B6', 'SR_B7']

# Load ESRI Land Cover data to use as labels
lc = ee.ImageCollection("projects/sat-io/open-datasets/landcover/ESRI_Global-LULC_10m").mosaic().clip(roi)

# Create a sample from the image with the land cover as labels
label = 'b1'  # Assuming 'b1' corresponds to the label in the ESRI dataset
sample = image.select(bands).addBands(lc.select(label)).sample(**{
    'region': roi,
    'numPixels': 1000,
    'seed': 0,
})

# Split the sample into training and validation sets
sample = sample.randomColumn('random')
trainingSample = sample.filter(ee.Filter.lte('random', 0.8))
validationSample = sample.filter(ee.Filter.gt('random', 0.8))

# Train a Random Forest classifier
classifier = ee.Classifier.smileRandomForest(10).train(
    features=trainingSample,
    classProperty=label,
    inputProperties=bands
)

# Classify the image
classified_image = image.select(bands).classify(classifier)

# Define a method for displaying Earth Engine Image tiles on a folium map
def add_ee_layer(self, ee_image_object, vis_params, name):
    map_id_dict = ee.Image(ee_image_object).getMapId(vis_params)
    folium.raster_layers.TileLayer(
        tiles=map_id_dict['tile_fetcher'].url_format,
        attr='Map Data &copy; <a href="https://earthengine.google.com/">Google Earth Engine</a>',
        name=name,
        overlay=True,
        control=True
    ).add_to(self)

# Add the method to the folium Map object
folium.Map.add_ee_layer = add_ee_layer

# Create a folium map centered on the ROI
Map = folium.Map(location=[center_lat, center_lon], zoom_start=8)

# Add base map
basemaps = {
    'Google Satellite Hybrid': folium.TileLayer(
        tiles='https://mt1.google.com/vt/lyrs=s&x={x}&y={y}&z={z}',
        attr='Google',
        name='Google Satellite Hybrid',
        overlay=True,
        control=True
    )
}
basemaps['Google Satellite Hybrid'].add_to(Map)

# Visualization parameters for the classified image
legend_dict = {
    "names": ["Water", "Trees", "Grass", "Flooded Vegetation", "Crops", "Scrub/Shrub", "Built-up", "Bare Ground", "Snow/Ice", "Clouds"],
    "colors": ["#1A5BAB", "#358221", "#A7D282", "#87D19E", "#FFDB5C", "#EECFA8", "#ED022A", "#EDE9E4", "#F2FAFF", "#C8C8C8"]
}

vis_params = {
    'min': 1,
    'max': 10,
    'palette': legend_dict['colors']
}

# Add the classified image to the map
Map.add_ee_layer(classified_image, vis_params, 'Land Cover Classification')

# Visualization parameters for Landsat image
vis_params_landsat = {
    'bands': ['SR_B4', 'SR_B3', 'SR_B2'],
    'min': 0,
    'max': 3000,
    'gamma': 1.4
}

# Add the Landsat image to the map
# Map.add_ee_layer(image, vis_params_landsat, 'Landsat 2021')s

# Add a legend to the map
legend_html = '''
<div style="position: fixed;
     bottom: 50px; left: 50px; width: 150px; height: 300px;
     background-color: white; z-index: 9999; font-size: 14px;">
     <b>Legend</b><br>
     <i style="background: #1A5BAB; width: 18px; height: 18px; float: left; margin-right: 5px"></i> Water<br>
     <i style="background: #358221; width: 18px; height: 18px; float: left; margin-right: 5px"></i> Trees<br>
     <i style="background: #A7D282; width: 18px; height: 18px; float: left; margin-right: 5px"></i> Grass<br>
     <i style="background: #87D19E; width: 18px; height: 18px; float: left; margin-right: 5px"></i> Flooded Vegetation<br>
     <i style="background: #FFDB5C; width: 18px; height: 18px; float: left; margin-right: 5px"></i> Crops<br>
     <i style="background: #EECFA8; width: 18px; height: 18px; float: left; margin-right: 5px"></i> Scrub/Shrub<br>
     <i style="background: #ED022A; width: 18px; height: 18px; float: left; margin-right: 5px"></i> Built-up<br>
     <i style="background: #EDE9E4; width: 18px; height: 18px; float: left; margin-right: 5px"></i> Bare Ground<br>
     <i style="background: #F2FAFF; width: 18px; height: 18px; float: left; margin-right: 5px"></i> Snow/Ice<br>
     <i style="background: #C8C8C8; width: 18px; height: 18px; float: left; margin-right: 5px"></i> Clouds<br>
</div>
'''
Map.get_root().html.add_child(folium.Element(legend_html))

# Add layer control and display the map
Map.add_child(folium.LayerControl())
folium_static(Map)





# import streamlit as st
# import ee
# import folium
# import geemap.colormaps as cm
# import geemap.foliumap as geemap
# from streamlit_folium import folium_static

# import ee

# # Authenticate the Google Earth Engine account
# ee.Authenticate()  

# # Initialize the Earth Engine API with your specific project ID
# ee.Initialize(project='lulc-429712')

# # Streamlit app
# st.title("Land Use Land Cover Map")

# # User inputs for latitude and longitude
# st.sidebar.header("Input Coordinates for ROI")
# latitude = st.sidebar.number_input("Latitude", value=18.2335, format="%.6f")
# longitude = st.sidebar.number_input("Longitude", value=72.892600, format="%.6f")

# # Define ROI using user inputs
# roi = ee.Geometry.Point([longitude, latitude])

# # Load Landsat 8 Collection 2 data and select relevant bands
# image = ee.ImageCollection('LANDSAT/LC08/C02/T1_L2') \
#     .filterBounds(roi) \
#     .filterDate('2021-01-01', '2021-12-31') \
#     .sort('CLOUD_COVER') \
#     .first()

# # Select bands for classification
# bands = ['SR_B2', 'SR_B3', 'SR_B4', 'SR_B5', 'SR_B6', 'SR_B7']

# # Load ESRI Land Cover data to use as labels
# lc = ee.ImageCollection("projects/sat-io/open-datasets/landcover/ESRI_Global-LULC_10m").mosaic().clip(image.geometry())

# # Create a sample from the image with the land cover as labels
# label = 'b1'  # Assuming 'b1' corresponds to the label in the ESRI dataset
# sample = image.select(bands).addBands(lc.select(label)).sample(**{
#     'region': image.geometry(),
#     'numPixels': 1000,
#     'seed': 0,
# })

# # Split the sample into training and validation sets into 80% and 20% respectively.
# sample = sample.randomColumn('random')
# trainingSample = sample.filter(ee.Filter.lte('random', 0.8))
# validationSample = sample.filter(ee.Filter.gt('random', 0.8))

# # Train a Random Forest classifier
# classifier = ee.Classifier.smileRandomForest(10).train(
#     features=trainingSample,
#     classProperty=label,
#     inputProperties=bands
# )

# # Classify the image
# classified_image = image.select(bands).classify(classifier)

# # Define a method for displaying Earth Engine Image tiles on a folium map
# def add_ee_layer(self, ee_image_object, vis_params, name):
#     map_id_dict = ee.Image(ee_image_object).getMapId(vis_params)
#     folium.raster_layers.TileLayer(
#         tiles=map_id_dict['tile_fetcher'].url_format,
#         attr='Map Data &copy; <a href="https://earthengine.google.com/">Google Earth Engine</a>',
#         name=name,
#         overlay=True,
#         control=True
#     ).add_to(self)

# # Add the method to the folium Map object
# folium.Map.add_ee_layer = add_ee_layer

# # Create a folium map centered on the ROI
# location = roi.centroid().coordinates().getInfo()[::-1]
# Map = folium.Map(location=location, zoom_start=8)

# # Add base map
# basemaps = {
#     'Google Satellite Hybrid': folium.TileLayer(
#         tiles='https://mt1.google.com/vt/lyrs=s&x={x}&y={y}&z={z}',
#         attr='Google',
#         name='Google Satellite Hybrid',
#         overlay=True,
#         control=True
#     )
# }
# basemaps['Google Satellite Hybrid'].add_to(Map)

# # Visualization parameters for the classified image
# legend_dict = {
#     "names": ["Water", "Trees", "Grass", "Flooded Vegetation", "Crops", "Scrub/Shrub", "Built-up", "Bare Ground", "Snow/Ice", "Clouds"],
#     "colors": ["#1A5BAB", "#358221", "#A7D282", "#87D19E", "#FFDB5C", "#EECFA8", "#ED022A", "#EDE9E4", "#F2FAFF", "#C8C8C8"]
# }

# vis_params = {
#     'min': 1,
#     'max': 10,
#     'palette': legend_dict['colors']
# }

# # Add the classified image to the map
# Map.add_ee_layer(classified_image, vis_params, 'Land Cover Classification')

# # Visualization parameters for Landsat image
# vis_params_landsat = {
#     'bands': ['SR_B4', 'SR_B3', 'SR_B2'],
#     'min': 0,
#     'max': 3000,
#     'gamma': 1.4
# }

# # Add the Landsat image to the map
# # Map.add_ee_layer(image, vis_params_landsat, 'Landsat 2021')

# # Add a legend to the map
# legend_html = '''
# <div style="position: fixed;
#      bottom: 50px; left: 50px; width: 150px; height: 300px;
#      background-color: white; z-index: 9999; font-size: 14px;">
#      <b>Legend</b><br>
#      <i style="background: #1A5BAB; width: 18px; height: 18px; float: left; margin-right: 5px"></i> Water<br>
#      <i style="background: #358221; width: 18px; height: 18px; float: left; margin-right: 5px"></i> Trees<br>
#      <i style="background: #A7D282; width: 18px; height: 18px; float: left; margin-right: 5px"></i> Grass<br>
#      <i style="background: #87D19E; width: 18px; height: 18px; float: left; margin-right: 5px"></i> Flooded Vegetation<br>
#      <i style="background: #FFDB5C; width: 18px; height: 18px; float: left; margin-right: 5px"></i> Crops<br>
#      <i style="background: #EECFA8; width: 18px; height: 18px; float: left; margin-right: 5px"></i> Scrub/Shrub<br>
#      <i style="background: #ED022A; width: 18px; height: 18px; float: left; margin-right: 5px"></i> Built-up<br>
#      <i style="background: #EDE9E4; width: 18px; height: 18px; float: left; margin-right: 5px"></i> Bare Ground<br>
#      <i style="background: #F2FAFF; width: 18px; height: 18px; float: left; margin-right: 5px"></i> Snow/Ice<br>
#      <i style="background: #C8C8C8; width: 18px; height: 18px; float: left; margin-right: 5px"></i> Clouds<br>
# </div>
# '''
# Map.get_root().html.add_child(folium.Element(legend_html))

# # Add layer control and display the map
# Map.add_child(folium.LayerControl())
# folium_static(Map)

