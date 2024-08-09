import streamlit as st
import geemap.foliumap as geemap
import ee

def app():
    st.title('Landsat Data and Tree Cover Changes Visualization')

    # Initialize the Earth Engine module
    ee.Initialize(project='lulc-429712')

    # Initialize the map
    m = geemap.Map(center=(22.5937, 78.9629), zoom=4, height=600)
    
    dataset = ee.Image("UMD/hansen/global_forest_change_2022_v1_10")
    dataset.bandNames()

    # Load and display the first Landsat image (2000)
    first_bands = ["first_b50", "first_b40", "first_b30"]
    first_image = dataset.select(first_bands)
    m.add_layer(first_image, {"bands": first_bands, "gamma": 1.5}, "Landsat 2000")

    # Load and display the last Landsat image (2022)
    last_bands = ["last_b50", "last_b40", "last_b30"]
    last_image = dataset.select(last_bands)
    m.add_layer(last_image, {"bands": last_bands, "gamma": 1.5}, "Landsat 2022")

    # Load and display tree cover data
    treecover = dataset.select(["treecover2000"])
    treeCoverVisParam = {"min": 0, "max": 100, "palette": ["black", "green"]}
    name = "Tree cover (%)"
    m.add_layer(treecover, treeCoverVisParam, name)
    m.add_colorbar(treeCoverVisParam, label=name, layer_name=name)

    # Add a basemap and tree cover loss/gain layers
    m.add_basemap("Esri.WorldImagery")
    treeloss = dataset.select(["loss"]).selfMask()
    treegain = dataset.select(["gain"]).selfMask()
    m.add_layer(treeloss, {"palette": "red"}, "Tree loss")
    m.add_layer(treegain, {"palette": "yellow"}, "Tree gain")

    # Display the map in Streamlit
    st.write(m.to_streamlit(height=700))

# Run the Streamlit app
if __name__ == "__main__":
    app()
