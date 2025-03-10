import streamlit as st
import ee
import geemap.foliumap as geemap
from datetime import datetime
from gee_utils import create_roi_province, get_indonesia_provinces
from landsat_utils import get_landsat_collection, get_visualization_params

# Streamlit Page Config
st.set_page_config(
    page_title="Landsat Imagery Generator",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Authenticate with Google Earth Engine (Service Account)
SERVICE_ACCOUNT = "gee-service-account@ee-dekagis.iam.gserviceaccount.com"
KEY_FILE = "ee-dekagis-cfe3874793f9.json"

@st.cache_resource
def initialize_gee():
    try:
        credentials = ee.ServiceAccountCredentials(SERVICE_ACCOUNT, KEY_FILE)
        ee.Initialize(credentials, project="ee-dekagis")
        return True
    except Exception as e:
        st.error(f"⚠️ Error initializing Google Earth Engine: {e}")
        return False

# Call GEE Initialization
gee_initialized = initialize_gee()

# Title
st.title("🌍 Landsat Imagery Generator")
st.markdown("Generate and visualize Landsat satellite imagery using Google Earth Engine.")

# Sidebar
with st.sidebar:
    st.header("⚙️ Settings")

    # Province selection
    provinces = get_indonesia_provinces()
    selected_province = st.selectbox("🌍 Select Province", provinces, index=0)

    # Year selection
    current_year = datetime.now().year
    year = st.slider("📅 Select Year", min_value=2013, max_value=current_year, value=2023)

    # Cloud cover
    cloud_cover = st.slider("☁️ Maximum Cloud Cover (%)", min_value=0, max_value=100, value=20)

    # Visualization type
    vis_types = ["true_color", "false_color"]
    vis_type = st.selectbox("🎨 Visualization Type", vis_types, index=0)

    # Generate button
    generate_button = st.button("🚀 Generate Imagery", type="primary")

# Cache ROI and Landsat Collection
@st.cache_data
def get_cached_roi(selected_province):
    return create_roi_province(selected_province)

@st.cache_data
def get_cached_landsat_collection(roi, year, cloud_cover):
    return get_landsat_collection(roi, year, cloud_cover)

# Map placeholder
map_placeholder = st.empty()

if generate_button and gee_initialized:
    with st.spinner("⏳ Processing..."):
        try:
            # Get cached ROI
            roi = get_cached_roi(selected_province)

            # Get cached Landsat collection
            landsat = get_cached_landsat_collection(roi, year, cloud_cover)

            # Check Landsat availability
            count = landsat.size().getInfo()

            if count == 0:
                st.warning(f"⚠️ No Landsat images found for {selected_province} in {year} with cloud cover < {cloud_cover}%. Try adjusting your filters.")
            else:
                # Get Landsat median image and clip it to the ROI
                median_image = landsat.median().clip(roi)

                # Get visualization parameters
                vis_params = get_visualization_params(vis_type)

                # Create a map
                m = geemap.Map()
                m.centerObject(roi, 11)

                # Add Landsat image to the map
                m.addLayer(median_image, vis_params, f'Landsat {vis_type.replace("_", " ").title()}')

                # Add boundary
                m.addLayer(roi, {'color': 'red'}, f'{selected_province} Boundary', False)

                # Display the map
                with map_placeholder:
                    m.to_streamlit(height=700, width=1200)

                # Show success message
                st.success(f"✅ Successfully generated Landsat imagery for {selected_province} ({year}) with {vis_type.replace('_', ' ')} visualization.")

        except Exception as e:
            st.error(f"❌ Error generating imagery: {e}")

else:
    # Show an empty map
    m = geemap.Map()
    with map_placeholder:
        m.to_streamlit(height=700, width=1200)

st.markdown("---")
st.markdown("📌 Data source: USGS/NASA Landsat 8 & 9")