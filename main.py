from fastapi import FastAPI
from pydantic import BaseModel

from processing.context_data import get_overpass_api_response
from processing.description import get_openai_api_response

app = FastAPI()


class Bbox(BaseModel):
    min_lon: float = -16.974
    min_lat: float = 27.986
    max_lon: float = -16.101
    max_lat: float = 28.595


class Chat(BaseModel):
    text: str = "Describe the history, climate, and landscape of the region."


@app.post("/context")
async def get_context_data(bbox: Bbox):
    context_data = await get_overpass_api_response(bbox)
    return context_data


@app.post("/description")
async def get_description(bbox: Bbox, chat: Chat):
    context_data = await get_overpass_api_response(bbox)
    description = await get_openai_api_response(data=context_data, chat=chat)
    return {"description": description}
