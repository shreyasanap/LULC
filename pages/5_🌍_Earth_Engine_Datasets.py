import ee
import json
import streamlit as st
import geemap.foliumap as geemap
import logging

st.set_page_config(layout="wide")

# Authenticate and initialize the Earth Engine API
ee.Authenticate()
ee.Initialize(project='lulc-429712')

def nlcd(Map):
    row1_col1, row1_col2 = st.columns([3, 1])
    width = 950
    height = 600

    years = ["2001", "2004", "2006", "2008", "2011", "2013", "2016", "2019"]

    def getNLCD(year):
        dataset = ee.ImageCollection("USGS/NLCD_RELEASES/2019_REL/NLCD")
        nlcd = dataset.filter(ee.Filter.eq("system:index", year)).first()
        landcover = nlcd.select("landcover")
        return landcover

    with row1_col2:
        selected_year = st.multiselect("Select a year", years)
        add_legend = st.checkbox("Show legend")

    if selected_year:
        for year in selected_year:
            Map.addLayer(getNLCD(year), {}, "NLCD " + year)

        if add_legend:
            Map.add_legend(
                legend_title="NLCD Land Cover Classification", builtin_legend="NLCD"
            )
        with row1_col1:
            Map.to_streamlit(width=width, height=height)

    else:
        with row1_col1:
            Map.to_streamlit(width=width, height=height)


def search_data(Map):
    if "ee_assets" not in st.session_state:
        st.session_state["ee_assets"] = None
    if "asset_titles" not in st.session_state:
        st.session_state["asset_titles"] = None

    col1, col2 = st.columns([2, 1])

    dataset = None
    with col2:
        popular_keywords = [
            "elevation", "land cover", "climate", "vegetation", "temperature",
            "precipitation", "water", "deforestation", "satellite"
        ]

        keyword = st.selectbox("Choose a keyword", popular_keywords, key="keyword_selectbox")
        custom_keyword = st.text_input("Or enter a custom keyword", "", key="custom_keyword_input")
        search_term = custom_keyword if custom_keyword else keyword

        if search_term:
            try:
                ee_assets = geemap.search_ee_data(search_term)
                asset_titles = [x["title"] for x in ee_assets]
                asset_types = [x["type"] for x in ee_assets]

                valid_ee_assets = []
                valid_titles = []

                for i, asset in enumerate(ee_assets):
                    try:
                        ee_id = asset["id"]
                        uid = asset["uid"]
                        asset_type = asset_types[i]

                        translate = {
                            "image_collection": "ee.ImageCollection('",
                            "image": "ee.Image('",
                            "table": "ee.FeatureCollection('",
                            "table_collection": "ee.FeatureCollection('",
                        }
                        ee_asset = f"{translate[asset_type]}{ee_id}')"

                        if ee_asset.startswith("ee.ImageCollection"):
                            ee_asset = ee.ImageCollection(ee_id)
                        elif ee_asset.startswith("ee.Image"):
                            ee_asset = ee.Image(ee_id)
                        elif ee_asset.startswith("ee.FeatureCollection"):
                            ee_asset = ee.FeatureCollection(ee_id)

                        Map.addLayer(ee_asset)
                        valid_ee_assets.append(asset)
                        valid_titles.append(asset["title"])
                    except Exception as e:
                        logging.error(f"Skipping dataset '{asset['title']}' due to error: {e}")

                st.session_state["ee_assets"] = valid_ee_assets
                st.session_state["asset_titles"] = valid_titles

                dataset = st.selectbox("Select a dataset", valid_titles, key="dataset_selectbox")

                if dataset is not None:
                    with st.expander("Show dataset details", True):
                        index = valid_titles.index(dataset)
                        html = geemap.ee_data_html(valid_ee_assets[index])
                        html = html.replace("\n", "")
                        st.markdown(html, True)

                    ee_id = valid_ee_assets[index]["id"]
                    uid = valid_ee_assets[index]["uid"]
                    st.markdown(f"""**Earth Engine Snippet:** `{ee_id}`""")
                    ee_asset = f"{translate[asset_types[index]]}{ee_id}')"

                    if ee_asset.startswith("ee.ImageCollection"):
                        ee_asset = ee.ImageCollection(ee_id)
                    elif ee_asset.startswith("ee.Image"):
                        ee_asset = ee.Image(ee_id)
                    elif ee_asset.startswith("ee.FeatureCollection"):
                        ee_asset = ee.FeatureCollection(ee_id)

                    vis_params = st.text_input(
                        "Enter visualization parameters as a dictionary", {}, key="vis_params_input"
                    )
                    layer_name = st.text_input("Enter a layer name", uid, key="layer_name_input")
                    button = st.button("Add dataset to map", key="add_layer_button")
                    if button:
                        vis = {}
                        try:
                            if vis_params.strip() == "":
                                vis_params = "{}"
                            vis = json.loads(vis_params.replace("'", '"'))
                            if not isinstance(vis, dict):
                                st.error("Visualization parameters must be a dictionary")
                            try:
                                Map.addLayer(ee_asset, vis, layer_name)
                            except Exception as e:
                                st.error(f"Error adding layer: {e}")
                        except Exception as e:
                            st.error(f"Invalid visualization parameters: {e}")

            except Exception as e:
                logging.error(f"Error searching Earth Engine data: {e}")

        with col1:
            Map.to_streamlit()


def app():
    st.title("Earth Engine Data Catalog")

    # Create the Map object only once
    Map = geemap.Map()

    apps = ["Search Earth Engine Data Catalog", "National Land Cover Database (NLCD)"]

    selected_app = st.selectbox("Select an app", apps)

    if selected_app == "National Land Cover Database (NLCD)":
        nlcd(Map)
    elif selected_app == "Search Earth Engine Data Catalog":
        search_data(Map)


app()
