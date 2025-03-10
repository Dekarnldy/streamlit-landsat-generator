import streamlit as st
import ee
import geemap.foliumap as geemap
from datetime import datetime
import io
from gee_utils import initialize_gee, create_roi_province, get_indonesia_provinces
from landsat_utils import get_landsat_collection, get_visualization_params

# page config
st.set_page_config(
    page_title="Landsat Imagery Generator",
    layout="wide",
    initial_sidebar_state="expanded"
)

# initialize Google Earth Engine
try:
    initialize_gee()
    gee_initialized = True
except Exception as e:
    st.error(f"Error initializing Google Earth Engine: {e}")
    gee_initialized = False

# title
st.title("Landsat Imagery Generator")
st.markdown("Generate and visualize Landsat satellite imagery using Google Earth Engine")

# sidebar
with st.sidebar:
    st.header("Settings")

    # province selection
    provinces = get_indonesia_provinces()
    selected_provinces = st.selectbox("Select Province", provinces, index=0)

    # year selection
    current_year = datetime.now().year
    year = st.slider("Select Year", min_value=2013, max_value=current_year, value=2023)

    # cloud cover
    cloud_cover = st.slider("Maximum Cloud Cover (%)", min_value=0, max_value=100, value=20)

    # visualization type
    vis_types = [
        "true_color", 
        "false_color", 
    ]
    vis_type = st.selectbox("Visualization Type", vis_types, index=0)

    # generate button
    generate_button = st.button("Generate Imagery", type="primary")

# map placeholder
with st.container():
    map_placeholder = st.empty()

if generate_button and gee_initialized:
    with st.spinner("Processing..."):
        try:
            # region of interest (ROI)
            roi = create_roi_province(selected_provinces)

            # get landsat collection
            landsat = get_landsat_collection(roi, year, cloud_cover)

            # check landsat availability
            count = landsat.size().getInfo()

            if count == 0:
                st.warning(f"No Landsat images found for {selected_provinces} in {year} with cloud cover < {cloud_cover}%. Try adjusting your filters.")
            else:
                # get landsat median image and clip it to the ROI
                median_image = landsat.median().clip(roi)

                # get visualization parameters based on selected visualization type
                vis_params = get_visualization_params(vis_type)

                # make a map
                m = geemap.Map()
                m.centerObject(roi, 11)

                # add landsat image to map
                m.addLayer(median_image, vis_params, f'Landsat {vis_type.replace("_", " ").title()}')

                # add boundary
                m.addLayer(roi, {'color': 'red'}, f'{selected_provinces} Boundary', False)

                # visualize a map
                with map_placeholder:
                    m.to_streamlit(height=700, width=1200)

                # show success message
                st.success(f"Successfully generated Landsat imagery for {selected_provinces} ({year}) with {vis_type.replace('_', ' ')} visualization.")

        except Exception as e:
            st.error(f"Error generating imagery: {e}")

else:
    # show empty map
    m = geemap.Map()
    with map_placeholder:
        m.to_streamlit(height=700, width=1200)

# Footer
st.markdown("---")
st.markdown("Data source: USGS/NASA Landsat 8 & 9")