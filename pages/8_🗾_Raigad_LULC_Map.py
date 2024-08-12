import ee
import streamlit as st
import geemap.foliumap as geemap

# Authenticate and initialize Earth Engine
try:
    ee.Initialize(project='lulc-429712')
    st.success("Earth Engine initialized successfully.")
except Exception as e:
    ee.Authenticate()
    ee.Initialize(project='lulc-429712')
    st.success("Earth Engine re-initialized after authentication.")

# Define coordinates for each class with numeric class values
def to_numeric_class(feature, class_mapping):
    # Convert the class property to numeric value
    return ee.Feature(
        feature.geometry(),
        feature.toDictionary().set('class', class_mapping.get(feature.get('class').getInfo(), -1))
    )

# Define class mappings (numeric values)
class_mapping = {
    'Builtup': 0,
    'Bareland': 1,
    'WaterBodies': 2,
    'Greenery': 3
}

# Define coordinates for each class
builtup_coords = [
    {"type": "Feature", "geometry": {"type": "Point", "coordinates": [73.03, 18.70]}, "properties": {"class": "Builtup"}},
    {"type": "Feature", "geometry": {"type": "Point", "coordinates": [73.11, 19.00]}, "properties": {"class": "Builtup"}},
    {"type": "Feature", "geometry": {"type": "Point", "coordinates": [73.11, 19.01]}, "properties": {"class": "Builtup"}},
    {"type": "Feature", "geometry": {"type": "Point", "coordinates": [73.13, 18.96]}, "properties": {"class": "Builtup"}},
    {"type": "Feature", "geometry": {"type": "Point", "coordinates": [72.89, 18.73]}, "properties": {"class": "Builtup"}},
    {"type": "Feature", "geometry": {"type": "Point", "coordinates": [73.36, 18.99]}, "properties": {"class": "Builtup"}},
    {"type": "Feature", "geometry": {"type": "Point", "coordinates": [73.09, 18.62]}, "properties": {"class": "Builtup"}},
    {"type": "Feature", "geometry": {"type": "Point", "coordinates": [73.27, 18.40]}, "properties": {"class": "Builtup"}},
    {"type": "Feature", "geometry": {"type": "Point", "coordinates": [73.25, 18.21]}, "properties": {"class": "Builtup"}},
    {"type": "Feature", "geometry": {"type": "Point", "coordinates": [73.29, 18.39]}, "properties": {"class": "Builtup"}},
    {"type": "Feature", "geometry": {"type": "Point", "coordinates": [73.02, 18.93]}, "properties": {"class": "Builtup"}},
]

bareland_coords = [
    {"type": "Feature", "geometry": {"type": "Point", "coordinates": [73.11, 18.98]}, "properties": {"class": "Bareland"}},
    {"type": "Feature", "geometry": {"type": "Point", "coordinates": [73.12, 18.98]}, "properties": {"class": "Bareland"}},
    {"type": "Feature", "geometry": {"type": "Point", "coordinates": [73.13, 18.98]}, "properties": {"class": "Bareland"}},
    {"type": "Feature", "geometry": {"type": "Point", "coordinates": [73.10, 18.97]}, "properties": {"class": "Bareland"}},
    {"type": "Feature", "geometry": {"type": "Point", "coordinates": [73.11, 18.97]}, "properties": {"class": "Bareland"}},
    {"type": "Feature", "geometry": {"type": "Point", "coordinates": [73.30, 18.40]}, "properties": {"class": "Bareland"}},
    {"type": "Feature", "geometry": {"type": "Point", "coordinates": [73.29, 18.40]}, "properties": {"class": "Bareland"}},
    {"type": "Feature", "geometry": {"type": "Point", "coordinates": [73.28, 18.40]}, "properties": {"class": "Bareland"}},
    {"type": "Feature", "geometry": {"type": "Point", "coordinates": [73.27, 18.40]}, "properties": {"class": "Bareland"}},
    {"type": "Feature", "geometry": {"type": "Point", "coordinates": [73.30, 18.25]}, "properties": {"class": "Bareland"}},
    {"type": "Feature", "geometry": {"type": "Point", "coordinates": [73.25, 18.23]}, "properties": {"class": "Bareland"}},
]

waterbodies_coords = [
    {"type": "Feature", "geometry": {"type": "Point", "coordinates": [73.18, 18.84]}, "properties": {"class": "WaterBodies"}},
    {"type": "Feature", "geometry": {"type": "Point", "coordinates": [73.92, 18.84]}, "properties": {"class": "WaterBodies"}},
    {"type": "Feature", "geometry": {"type": "Point", "coordinates": [73.07, 18.74]}, "properties": {"class": "WaterBodies"}},
    {"type": "Feature", "geometry": {"type": "Point", "coordinates": [73.11, 18.99]}, "properties": {"class": "WaterBodies"}},
    {"type": "Feature", "geometry": {"type": "Point", "coordinates": [73.09, 19.00]}, "properties": {"class": "WaterBodies"}},
    {"type": "Feature", "geometry": {"type": "Point", "coordinates": [73.11, 18.98]}, "properties": {"class": "WaterBodies"}},
    {"type": "Feature", "geometry": {"type": "Point", "coordinates": [73.04, 18.92]}, "properties": {"class": "WaterBodies"}},
    {"type": "Feature", "geometry": {"type": "Point", "coordinates": [73.04, 18.91]}, "properties": {"class": "WaterBodies"}},
    {"type": "Feature", "geometry": {"type": "Point", "coordinates": [73.04, 18.90]}, "properties": {"class": "WaterBodies"}},
    {"type": "Feature", "geometry": {"type": "Point", "coordinates": [72.96, 18.56]}, "properties": {"class": "WaterBodies"}},
    {"type": "Feature", "geometry": {"type": "Point", "coordinates": [72.97, 18.56]}, "properties": {"class": "WaterBodies"}},
    {"type": "Feature", "geometry": {"type": "Point", "coordinates": [72.99, 18.79]}, "properties": {"class": "WaterBodies"}},
    {"type": "Feature", "geometry": {"type": "Point", "coordinates": [72.99, 18.76]}, "properties": {"class": "WaterBodies"}},
    {"type": "Feature", "geometry": {"type": "Point", "coordinates": [73.00, 18.99]}, "properties": {"class": "WaterBodies"}},
    {"type": "Feature", "geometry": {"type": "Point", "coordinates": [73.07, 19.00]}, "properties": {"class": "WaterBodies"}},
]

greenery_coords = [
    {"type": "Feature", "geometry": {"type": "Point", "coordinates": [73.10, 18.99]}, "properties": {"class": "Greenery"}},
    {"type": "Feature", "geometry": {"type": "Point", "coordinates": [73.12, 18.99]}, "properties": {"class": "Greenery"}},
    {"type": "Feature", "geometry": {"type": "Point", "coordinates": [73.10, 18.87]}, "properties": {"class": "Greenery"}},
    {"type": "Feature", "geometry": {"type": "Point", "coordinates": [73.06, 18.87]}, "properties": {"class": "Greenery"}},
    {"type": "Feature", "geometry": {"type": "Point", "coordinates": [73.06, 18.85]}, "properties": {"class": "Greenery"}},
    {"type": "Feature", "geometry": {"type": "Point", "coordinates": [73.08, 18.96]}, "properties": {"class": "Greenery"}},
    {"type": "Feature", "geometry": {"type": "Point", "coordinates": [72.94, 18.55]}, "properties": {"class": "Greenery"}},
    {"type": "Feature", "geometry": {"type": "Point", "coordinates": [72.94, 18.56]}, "properties": {"class": "Greenery"}},
    {"type": "Feature", "geometry": {"type": "Point", "coordinates": [72.99, 18.55]}, "properties": {"class": "Greenery"}},
    {"type": "Feature", "geometry": {"type": "Point", "coordinates": [72.99, 18.53]}, "properties": {"class": "Greenery"}},
    {"type": "Feature", "geometry": {"type": "Point", "coordinates": [72.91, 18.83]}, "properties": {"class": "Greenery"}},
]

# Combine all into one FeatureCollection and convert class labels to numeric
combined_coords = builtup_coords + bareland_coords + waterbodies_coords + greenery_coords
features = [ee.Feature(ee.Geometry.Point(c['geometry']['coordinates']), c['properties']) for c in combined_coords]
numeric_coords = [to_numeric_class(feature, class_mapping) for feature in features]
training_fc = ee.FeatureCollection(numeric_coords)

# Define the district boundary
districts = ee.FeatureCollection("projects/ee-laxmisneha21comp/assets/india_district")
raigad_boundary = districts.filter(ee.Filter.And(
    ee.Filter.eq('district', 'Raigarh'),
    ee.Filter.eq('st_nm', 'Maharashtra')
))

# Define the Landsat 8 Image Collection
s2 = ee.ImageCollection("LANDSAT/LC08/C02/T1_RT")

# Before (Oct 2023 - Dec 2023)
before = s2.filter(ee.Filter.bounds(raigad_boundary)) \
           .filter(ee.Filter.date('2023-10-01', '2023-12-30')) \
           .filter(ee.Filter.lt('CLOUD_COVER', 10)) \
           .select('B.*') \
           .median() \
           .clip(raigad_boundary)

# Extract training data
training_data = before.sampleRegions(
    collection=training_fc,
    properties=['class'],
    scale=30
)

# Train a classifier
classifier = ee.Classifier.smileRandomForest(numberOfTrees=50).train(
    features=training_data,
    classProperty='class',
    inputProperties=before.bandNames()
)

# Classify the image
classified = before.classify(classifier)

# Define visualization parameters for LULC
lulc_viz = {
    'min': 0,
    'max': 3,  # Adjust according to the number of classes
    'palette': ['red', 'yellow', 'blue', 'green']  # Adjust colors for your classes
}

# Create a map
Map = geemap.Map()

# Add the layers to the map
Map.addLayer(raigad_boundary, {'color': 'grey'}, 'Boundary')
Map.addLayer(before, {'bands': ['B4', 'B3', 'B2'], 'min': 0, 'max': 3000}, 'Before')
Map.addLayer(classified, lulc_viz, 'LULC Classification')

# Set the center of the map
Map.centerObject(raigad_boundary, 10)

# Display the map
st.title("Land Cover Classification using Landsat 8 Imagery and GEE")
st.write("Raigad District, Maharashtra")
Map.to_streamlit(height=700)
