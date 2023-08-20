import requests
import streamlit as st
from pydantic import BaseModel
from shapely import Polygon
from streamlit_folium import st_folium

from geo_describer_ai.map import FoliumMap
from geo_describer_ai.verification import selected_bbox_too_large, selected_bbox_in_boundary

st.set_page_config(
    page_title="mapa",
    page_icon=":earth_africa:",
    layout="wide",
    initial_sidebar_state="expanded"
)

MAP_CENTER = [25.0, 55.0]
MAP_ZOOM = 3
MAX_ALLOWED_AREA_SIZE = 25.0
BTN_LABEL = "Submit"
API_BASE_URL = "http://localhost:3000"


# Define the models for the input data:
class Bbox(BaseModel):
    min_lon: float
    min_lat: float
    max_lon: float
    max_lat: float


class Chat(BaseModel):
    text: str


def login(username, password):
    response = requests.post(f"{API_BASE_URL}/login", data={"username": username, "password": password})
    if response.status_code == 200:
        token = response.json()["access_token"]
        return token
    else:
        st.error("Invalid credentials. Please try again.")
        return None


def login_page():
    st.subheader("Login")
    username = st.text_input("Username")
    password = st.text_input("Password", type="password")
    if st.button("Login"):
        token = login(username, password)
        if token:
            st.session_state.token = token
            st.success("Logged in successfully")
            main()


def display_context_data(bbox_data):
    st.subheader("Context Data")
    response = requests.post(f"{API_BASE_URL}/context", json=bbox_data.dict())
    if response.status_code == 200:
        context_data = response.json()
        st.json(context_data)
    else:
        st.error("Error retrieving context data. Please try again.")


def display_description(bbox_data, chat_data):
    st.subheader("Description")
    headers = {"Authorization": f"Bearer {st.session_state.token}"}
    response = requests.post(f"{API_BASE_URL}/description", json={"bbox": bbox_data.dict(), "chat": chat_data.dict()},
                             headers=headers)
    if response.status_code == 200:
        description = response.json()["description"]
        st.write(description)
    elif response.status_code == 401:  # Unauthorized
        st.warning("Your session has expired. Please log in again.")
    else:
        st.error("Error retrieving description. Please try again.")


# Create the Streamlit app and define the main code:
def main():
    if "token" not in st.session_state:
        login_page()
        return
    st.title(":earth_africa: GeoDescriber API Demo")

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
        # Getting started
        st.subheader("Getting Started")
        st.markdown(
            f"""
                        1. Click the black square on the map
                        2. Draw a rectangle on the map
                        3. Provide your description request in the textbox below
                        4. Click on <kbd>{BTN_LABEL}</kbd>
                        5. Wait for the computation to finish
                        """,
            unsafe_allow_html=True,
        )

        # Input form for chat text
        st.subheader("Chat Text")
        chat_form = st.form(key="chat_form")
        chat_text = chat_form.text_area("What do you want me to describe about this region? :thinking_face:",
                                        value="Describe the history, climate, and landscape of the region.")
        submit_chat = chat_form.form_submit_button("Submit", disabled=False if geojson is not None else True)

        # Display results upon submission
        if geojson or submit_chat:
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
                # Create a Shapely polygon from the coordinates
                poly = Polygon(geojson['geometry']['coordinates'][0])
                # Get the bbox coordinates using the bounds() method
                min_lon, min_lat, max_lon, max_lat = poly.bounds

                bbox_data = Bbox(min_lon=min_lon, min_lat=min_lat, max_lon=max_lon, max_lat=max_lat)
                chat_data = Chat(text=chat_text)

                if geojson and not submit_chat:
                    display_context_data(bbox_data)
                if submit_chat:
                    display_description(bbox_data, chat_data)
                    # Display success message in the sidebar
                    st.sidebar.success("Successfully created description!")


if __name__ == "__main__":
    main()
