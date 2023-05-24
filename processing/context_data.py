from typing import List

import overpy
from pydantic import BaseModel


class ContextData(BaseModel):
    elements: List


async def get_overpass_api_response(bbox):
    # transform bbox
    bounds = [bbox.min_lat, bbox.min_lon, bbox.max_lat, bbox.max_lon]
    bbox = ",".join(str(x) for x in bounds)

    # create Overpass API query
    api = overpy.Overpass()

    # define query
    query = """
        [out:json];
        (
          node["place"="island"]({bbox});
          node["place"="city"]({bbox});
          node["place"="town"]({bbox});
          node["place"="village"]({bbox});
          relation["leisure"="nature_reserve"]["protect_class"="2"]({bbox});
          relation["leisure"="nature_reserve"]["protect_class"="6"]({bbox});
        );
        out center;
    """.format(bbox=bbox)

    # execute query and get results
    try:
        result = api.query(query)
    except Exception as e:
        return {"error": str(e)}

    # Top cities and protected_areas
    top_cities_towns = _get_top_elements(elements=result.nodes, desired_keys=['name', 'place', 'population', 'ele'],
                                         sort_by="place", order=["island", "city", "town", "village"])
    top_protected_area = _get_top_elements(elements=result.relations, desired_keys=['name', 'protection_title', "protect_class", 'boundary'],
                                           sort_by="protect_class", order=["2", "6"])

    context_data = ContextData(elements=top_cities_towns + top_protected_area)

    return context_data


def _get_top_elements(elements, desired_keys, n_elements=20, sort_by=None, order=None):
    # create a list of main element tags
    elements_list = []

    # iterate over the elements in the result
    for element in elements:
        element_tags = element.tags
        element_data = {key: value for key, value in element_tags.items() if key in desired_keys}
        if type(element) == overpy.Node:
            element_data['lat'] = float(element.lat)
            element_data['lon'] = float(element.lon)
            element_data['type'] = 'node'
        elif type(element) == overpy.Relation:
            element_data['center'] = {
                'lat': float(element.center_lat),
                'lon': float(element.center_lon)}
            element_data['type'] = 'relation'

        # Add the element to the list
        elements_list.append(element_data)

    # Sort elements
    if sort_by:
        elements_list = sorted(elements_list, key=lambda x: order.index(x[sort_by]))

    return elements_list[:n_elements]