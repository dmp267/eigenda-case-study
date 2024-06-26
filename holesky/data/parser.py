import os
import geopandas as gpd
from pykml import parser
from shapely import Polygon, MultiPolygon


def parse_kwargs(data):
    """
    Parse the KML file and return the necessary kwargs for the geo_temporal_query function.

    Parameters:
        data (str or file-like object): The KML file.
    
    Returns:    
        dict: The kwargs for the geo_temporal_query function.
    """
    if os.path.exists(data):
        with open(data, 'r', encoding='utf-8') as f:
            root = parser.parse(f).getroot()
            f.close()
    else:
        try:
            root = parser.parse(data).getroot()
        except:
            raise ValueError("Invalid data provided.")
            
    polygons_mask = []
    for folder in root.Document.Folder:
        for placemark in folder.Placemark:
            print(f'Processing {placemark.name.text.strip()}')

            multigeometry = placemark.MultiGeometry
            multipolygons = []

            for polygon in multigeometry.Polygon:
                coordinates = polygon.outerBoundaryIs.LinearRing.coordinates.text.strip()
                coordinate_pairs = []

                for coord in coordinates.split():
                    lon, lat, alt = coord.split(',')
                    if int(alt) != 0:
                        print(f'Warning: altitude is not zero: {alt}')
                    coordinate_pairs.append((float(lon), float(lat)))
                multipolygons.append(Polygon(coordinate_pairs))
            polygons_mask.append(MultiPolygon(multipolygons))

    polygon_kwargs = { "polygons_mask": gpd.array.from_shapely(polygons_mask) }
    spatial_agg_kwargs = { "agg_method": "sum" }
    # temporal_agg_kwargs = { "time_period": "day", "agg_method": "sum" }
    temporal_agg_kwargs = None

    return {
        "polygon_kwargs": polygon_kwargs,
        "spatial_agg_kwargs": spatial_agg_kwargs,
        "temporal_agg_kwargs": temporal_agg_kwargs
    }
