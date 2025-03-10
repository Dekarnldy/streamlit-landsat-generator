import ee
import geemap

def initialize_gee():
    ee.Authenticate()
    ee.Initialize(project="ee-dekagis")


def create_roi_province(province_name):
    roi = ee.FeatureCollection("FAO/GAUL/2015/level1") \
        .filter(ee.Filter.eq('ADM0_NAME', "Indonesia")) \
        .filter(ee.Filter.eq('ADM1_NAME', province_name))
    return roi

def get_indonesia_provinces():
    try:
        provinces = ee.FeatureCollection("FAO/GAUL/2015/level1") \
            .filter(ee.Filter.eq("ADM0_NAME", "Indonesia"))
        province_list = provinces.aggregate_array('ADM1_NAME').getInfo()
        return sorted(province_list)
    except:
        return ["Aceh", "Bali", "Banten", "Bengkulu", "DI Yogyakarta", 
                "DKI Jakarta", "Gorontalo", "Jambi", "Jawa Barat", "Jawa Tengah",
                "Jawa Timur", "Kalimantan Barat", "Kalimantan Selatan", "Kalimantan Tengah",
                "Kalimantan Timur", "Kalimantan Utara", "Kepulauan Bangka Belitung",
                "Kepulauan Riau", "Lampung", "Maluku", "Maluku Utara", "Nusa Tenggara Barat",
                "Nusa Tenggara Timur", "Papua", "Papua Barat", "Papua Pegunungan",
                "Papua Tengah", "Papua Selatan", "Papua Barat Daya", "Riau", 
                "Sulawesi Barat", "Sulawesi Selatan", "Sulawesi Tengah", "Sulawesi Tenggara",
                "Sulawesi Utara", "Sumatera Barat", "Sumatera Selatan", "Sumatera Utara"]

print(get_indonesia_provinces()) 
