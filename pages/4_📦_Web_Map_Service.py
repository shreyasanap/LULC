import json
import streamlit as st
import leafmap.foliumap as leafmap

st.set_page_config(layout="wide")

# Define a whitelist of trusted URLs
trusted_urls = [
    "https://services.terrascope.be/wms/v2",
    # Add more trusted URLs here
]

# Exclude specific layers
excluded_layers = [
    "TERRASCOPE_S2_CHLA_V1", "TERRASCOPE_S2_CHL_V1", "TERRASCOPE_S2_RHOW_V1", 
    "TERRASCOPE_S2_SPM_V1", "TERRASCOPE_S2_TUR_V1"
]

@st.cache_data
def get_layers(url):
    try:
        options = leafmap.get_wms_layers(url)
        # Filter layers to include only those starting with "WORLDCOVER", "TERRASCOPE", or "CGS_S1_COHERENCE"
        filtered_options = [
            layer for layer in options 
            if (layer.startswith("WORLDCOVER") or layer.startswith("TERRASCOPE") or layer == "CGS_S1_COHERENCE")
            and layer not in excluded_layers
        ]
        return filtered_options
    except Exception as e:
        st.error(f"Error retrieving layers: {e}")
        return []

def is_trusted_url(url):
    return url in trusted_urls

def app():
    st.title("Web Map Service (WMS)")
    st.markdown(
        """
    This app is a demonstration of loading Web Map Service (WMS) layers. Simply enter the URL of the WMS service
    in the text box below and press Enter to retrieve the layers. Go to https://apps.nationalmap.gov/services to find
    some WMS URLs if needed.
    """
    )

    row1_col1, row1_col2 = st.columns([3, 1.3])
    width = 800
    height = 600
    layers = None

    with row1_col2:
        esa_landcover = "https://services.terrascope.be/wms/v2"
        url = st.text_input(
            "Enter a WMS URL:", value="https://services.terrascope.be/wms/v2"
        )
        empty = st.empty()

        if url:
            if is_trusted_url(url):
                options = get_layers(url)
                if not options:
                    st.warning("No layers found or unable to fetch layers from the URL.")
                    options = []
            else:
                st.error(
                    "The entered URL is not trusted. Please enter a valid WMS URL."
                )
                options = []

            default = None
            if url == esa_landcover:
                default = "WORLDCOVER_2020_MAP"
            layers = empty.multiselect(
                "Select WMS layers to add to the map:", options, default=default
            )
            add_legend = st.checkbox("Add a legend to the map", value=True)
            if default == "WORLDCOVER_2020_MAP":
                legend = str(leafmap.builtin_legends["ESA_WorldCover"])
            else:
                legend = ""
            if add_legend:
                legend_text = st.text_area(
                    "Enter a legend as a dictionary {label: color}",
                    value=legend,
                    height=200,
                )

        with row1_col1:
            # Set the map to start zoomed in on India
            m = leafmap.Map(center=(20.5937, 78.9629), zoom=5)

            if layers is not None:
                for layer in layers:
                    try:
                        m.add_wms_layer(
                            url, layers=layer, name=layer, attribution=" ", transparent=True
                        )
                    except Exception as e:
                        st.error(f"Error adding layer '{layer}': {e}")

            if add_legend and legend_text:
                try:
                    legend_dict = json.loads(legend_text.replace("'", '"'))
                    m.add_legend(legend_dict=legend_dict)
                except json.JSONDecodeError:
                    st.error("Invalid legend format. Please enter a valid JSON dictionary.")

            m.to_streamlit(height=height)

app()
