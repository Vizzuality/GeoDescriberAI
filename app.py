import json

import tiktoken
import streamlit as st
from streamlit_folium import st_folium

from geo_describer_ai.map import FoliumMap
from geo_describer_ai.utils import get_bbox
from geo_describer_ai.apis import get_overpass_api_response, get_openai_api_response
from geo_describer_ai.verification import selected_bbox_in_boundary, selected_bbox_too_large


MAP_CENTER = [25.0, 55.0]
MAP_ZOOM = 3
MAX_ALLOWED_AREA_SIZE = 25.0
BTN_LABEL = "Describe"

if __name__ == "__main__":
    st.set_page_config(
        page_title="mapa",
        page_icon=":earth_africa:",
        layout="wide",
        initial_sidebar_state="expanded"
    )
    st.title(":earth_africa: Map to describe a region!")

    st.write(
        """Hello! I'm GeoDescriberAI, a Geospatial AI assistant that describes any location.""")

    m = FoliumMap(center=MAP_CENTER, zoom=MAP_ZOOM)

    output = st_folium(m, key="init", width=1300, height=600)

    geojson = None
    if output["all_drawings"] is not None:
        if len(output["all_drawings"]) != 0:
            if output["last_active_drawing"] is not None:
                # get latest modified drawing
                geojson = output["last_active_drawing"]


    # ensure progress bar resides at top of sidebar and is invisible initially
    progress_bar = st.sidebar.progress(0)
    progress_bar.empty()

    # Getting Started container
    with st.sidebar.container():
        st.markdown(
            f"""
                # Getting Started
                1. Click the black square on the map
                2. Draw a rectangle on the map
                3. Provide your description request in the textbox below
                4. Click on <kbd>{BTN_LABEL}</kbd>
                5. Wait for the computation to finish
                """,
            unsafe_allow_html=True,
        )

        # Create input text area
        chat = st.text_area("What do you want me to describe about this region? :thinking_face:")

        # Create an empty container for the description
        # Display description of the region
        st.markdown(
            f"""
                            ### Description of the region:
                            """,
            unsafe_allow_html=True,
        )

        text_container = st.empty()

        # Add the button and its callback
        if st.button(BTN_LABEL,
                     key="describe",
                     disabled=False if geojson is not None else True):

            # Check if the geometry is valid
            geometry = geojson['geometry']
            if selected_bbox_too_large(geometry, threshold=MAX_ALLOWED_AREA_SIZE):
                st.sidebar.warning(
                    "Selected region is too large, fetching data for this area would consume too many resources. "
                    "Please select a smaller region."
                )
            elif not selected_bbox_in_boundary(geometry):
                st.sidebar.warning(
                    "Selected rectangle is not within the allowed region of the world map. "
                    "Do not scroll too far to the left or right. "
                    "Ensure to use the initial center view of the world for drawing your rectangle."
                )
            else:
                # Get the bbox
                bbox = get_bbox(geojson)

                # Get the Overpass API response containing the main locations
                overpass_response = get_overpass_api_response(bbox)

                # Check context length tokens
                # Create a tokenizer
                ENC = tiktoken.encoding_for_model("text-davinci-003")
                context_length = len(ENC.encode(f"""contextual data: {json.dumps(overpass_response)}""")) - 589

                if context_length > 4097:
                    st.sidebar.warning(
                        "The API response is too long for me to read. Please select a smaller region."
                    )
                else:
                    # Get the OpenAI API response containing the description
                    description = get_openai_api_response(data=overpass_response, chat=chat)

                    text_container.markdown(
                        f"""
                        {description}
                        """,
                        unsafe_allow_html=True,
                    )

                    # Display success message in the sidebar
                    st.sidebar.success("Successfully created description!")

