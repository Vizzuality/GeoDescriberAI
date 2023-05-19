from shapely import Polygon


def get_bbox(geojson: dict) -> str:
    # Create a Shapely polygon from the coordinates
    poly = Polygon(geojson['geometry']['coordinates'][0])
    # Get the bbox coordinates using the bounds() method
    min_x, min_y, max_x, max_y = poly.bounds
    bounds = [min_y, min_x, max_y, max_x]
    bbox = ",".join(str(x) for x in bounds)
    return bbox
