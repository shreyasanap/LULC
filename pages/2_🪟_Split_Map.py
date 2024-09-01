import streamlit as st
import geemap.foliumap as geemap
import ee

def app():
    st.title('Split Map of Land Cover Changes')

    # Initialize the Earth Engine module
    ee.Initialize(project='lulc-429712')

    # Define available years
    years = [str(year) for year in range(2001, 2022, 2)]

    # Dropdowns for year selection
    left_year = st.selectbox("Select Year for Left Side", years, index=years.index('2003'))
    right_year = st.selectbox("Select Year for Right Side", years, index=years.index('2021'))

    # Initialize the map
    m = geemap.Map(center=(22.5937, 78.9629), zoom=4, height=600)

    # Define a function to load MODIS land cover data
    def get_modis_layer(year):
        start_date = f'{year}-01-01'
        end_date = f'{year}-12-31'
        modis = ee.ImageCollection("MODIS/061/MCD12C1") \
            .filter(ee.Filter.date(start_date, end_date)) \
            .first().select('Majority_Land_Cover_Type_1')
        return geemap.ee_tile_layer(modis, landcover_vis, f"MODIS Land Cover {year}")

    # Visualization parameters
    landcover_vis = {
        'min': 0,
        'max': 16,
        'palette': [
            '1c0dff', '05450a', '086a10', '54a708', '78d203', '009900', 'c6b044', 'dcd159',
            'dade48', 'fbff13', 'b6ff05', '27ff87', 'c24f44', 'a5a5a5', 'ff6d4c', '69fff8', 'f9ffa4'
        ]
    }

    # Create tile layers for the selected years
    left_layer = get_modis_layer(left_year)
    right_layer = get_modis_layer(right_year)

    # Add the layers to the split map
    m.split_map(left_layer, right_layer)

    # Convert the map to HTML
    map_html = m.to_html()

    # Display the map in Streamlit
    st.components.v1.html(map_html, height=700)

    # Define and display the legend
    legend = {
        'Water': '1c0dff',
        'Forest': '05450a',
        'Grassland': '086a10',
        'Cropland': '54a708',
        'Urban': '78d203',
        'Barren': '009900',
        'Savanna': 'c6b044',
        'Shrubland': 'dcd159',
        'Wetland': 'dade48',
        'Snow/Ice': 'fbff13',
        'Tundra': 'b6ff05',
        'Mangroves': '27ff87',
        'Built-up': 'c24f44',
        'Agricultural': 'a5a5a5',
        'Desert': 'ff6d4c',
        'Unknown': '69fff8',
        'Other': 'f9ffa4'
    }

    legend_html = '<div style="display: flex; flex-direction: column; margin-top: 20px;">'
    for label, color in legend.items():
        legend_html += f'<div style="display: flex; align-items: center; margin-bottom: 5px;"><div style="width: 20px; height: 20px; background-color: #{color}; margin-right: 5px;"></div><span>{label}</span></div>'
    legend_html += '</div>'

    st.markdown(legend_html, unsafe_allow_html=True)

# Run the Streamlit app
if __name__ == "__main__":
    app()
