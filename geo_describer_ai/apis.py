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
          node["place"="city"]({bbox});
          node["place"="town"]({bbox});
          //relation["leisure"="nature_reserve"]["protect_class"="1"]({bbox});
          relation["leisure"="nature_reserve"]["protect_class"="2"]({bbox});
          relation["leisure"="nature_reserve"]["protect_class"="6"]({bbox});
        );
        out center;
    """.format(bbox=bbox)

    # execute query and get results
    result = api.query(query)

    # Top cities and protected_areas
    top_cities_towns = _get_top_elements(result.nodes, "population", 5, reverse=True)
    top_protected_area = _get_top_elements(result.relations, "protect_class", 8)

    overpass_response = {'elements': top_cities_towns + top_protected_area}

    return overpass_response


def _get_top_elements(elements, tag_key, num_elements, reverse=False):
    # create a list of main element tags
    tags_list = []

    # iterate over the elements in the result
    for element in elements:
        element_data = {
            'id': element.id,
            'tags': element.tags
        }
        if type(element) == overpy.Node:
            element_data['lat'] = float(element.lat)
            element_data['lon'] = float(element.lon)
            element_data['type'] = 'node'
        elif type(element) == overpy.Relation:
            element_data['center'] = {
                'lat': float(element.center_lat),
                'lon': float(element.center_lon)}
            element_data['type'] = 'relation'

        # get the tag value for the specified key
        tag_value = element.tags.get(tag_key)
        if tag_value is not None:
            # convert the tag value to the appropriate data type (e.g., int, str)
            try:
                tag_value = int(tag_value)
            except ValueError:
                pass

            # add the element and its tag value to the list
            tags_list.append((element_data, tag_value))

    # sort the list based on the tag value
    tags_list.sort(key=lambda x: x[1], reverse=reverse)

    # get the top elements with the largest tag value
    top_elements = tags_list[:num_elements]

    # create a list of tags from the top elements
    top_elements_tags = [tags for tags, value in top_elements]

    return top_elements_tags


