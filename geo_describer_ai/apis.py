import os
import json

import overpy
from dotenv import load_dotenv
from langchain.chat_models import ChatOpenAI
from langchain.schema import HumanMessage, SystemMessage, AIMessage

SYSTEM_MESSAGE = """You are an environmental scientist that will generate a detailed description of a region based on the prompt starting with 'request: ' and the locations provided as 'contextual data'.
Your description should sound like it was spoken by someone with personal knowledge of the region. 
Format any names or places you get as bold text in Markdown.
Do not mention who you are or the Overpass API, just give the description of the place."""

# take environment variables from .env.
load_dotenv()

openai_api_key = os.getenv("OPENAI_API_KEY")


def get_openai_api_response(data, chat):
    request = f"request: {chat}"
    context = f"""contextual data: {json.dumps(data)}"""

    chat = ChatOpenAI(temperature=.7, openai_api_key=openai_api_key)

    chat_response = chat(
        [
            SystemMessage(content=SYSTEM_MESSAGE),
            AIMessage(content=context),
            HumanMessage(content=request)
        ]
    )

    description = chat_response.content

    return description


def get_overpass_api_response(bbox):
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
    result = api.query(query)

    # Top cities and protected_areas
    top_cities_towns = _get_top_elements(elements=result.nodes, desired_keys=['name', 'place', 'population', 'ele'],
                                         sort_by="place", order=["island", "city", "town", "village"])
    top_protected_area = _get_top_elements(elements=result.relations, desired_keys=['name', 'protection_title', "protect_class", 'boundary'],
                                           sort_by="protect_class", order=["2", "6"])

    overpass_response = {'elements': top_cities_towns + top_protected_area}

    return overpass_response


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





