import ee
import geemap

def get_landsat_collection(roi, year, max_cloud_cover=5):

    start_date = ee.Date.fromYMD(year, 1, 1)
    end_date = ee.Date.fromYMD(year, 12, 31)

    landsat_8 = ee.ImageCollection("LANDSAT/LC08/C02/T1_TOA") \
        .filterBounds(roi) \
        .filterDate(start_date, end_date) \
        .filter(ee.Filter.lt('CLOUD_COVER', max_cloud_cover))\
        .select(["B4", "B3", "B2", "B5"])

    landsat_9 = ee.ImageCollection("LANDSAT/LC09/C02/T1_TOA") \
        .filterBounds(roi) \
        .filterDate(start_date, end_date) \
        .filter(ee.Filter.lt('CLOUD_COVER', max_cloud_cover))\
        .select(["B4", "B3", "B2", "B5"])

    # combine Landsat 8 and 9
    if year >= 2021:
        landsat_combined = landsat_8.merge(landsat_9)
        return landsat_combined
    else:
        return landsat_8

#visualization
def get_visualization_params(vis_type="true_color"):
    
    vis_params = {
        "true_color": {
            'bands': ['B4', 'B3', 'B2'],
            'min': 0,
            'max': 0.3,
            'gamma': 1.4
        },
        "false_color": {
            'bands': ['B5', 'B4', 'B3'],
            'min': 0,
            'max': 0.3,
            'gamma': 1.4
        },
    }
    
    return vis_params.get(vis_type, vis_params["true_color"])
