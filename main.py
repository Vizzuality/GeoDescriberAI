from fastapi import FastAPI
from fastapi.params import Depends
from pydantic import BaseModel

from database.repository import get_mongo_repository
from processing.context_data import get_overpass_api_response
from processing.description import get_openai_api_response
from questions_answers.repository import QuestionAnswerRepository, get_qa_repository

app = FastAPI()
mongo_repository = get_mongo_repository()


class Bbox(BaseModel):
    min_lon: float = -16.974
    min_lat: float = 27.986
    max_lon: float = -16.101
    max_lat: float = 28.595


class Chat(BaseModel):
    text: str = "Describe the history, climate, and landscape of the region."


@app.on_event("startup")
async def startup_event():
    print("Starting up...")
    is_connected = await mongo_repository.test_connection()
    if is_connected:
        print("Connected to MongoDB")
    else:
        print("Failed to connect to MongoDB")
        # You may want to add logic here to handle the failed connection, like raising an exception or shutting down the application.


@app.post("/context")
async def get_context_data(bbox: Bbox):
    context_data = await get_overpass_api_response(bbox)
    return context_data


@app.post("/description")
async def get_description(bbox: Bbox, chat: Chat, repo: QuestionAnswerRepository = Depends(get_qa_repository)):
    context_data = await get_overpass_api_response(bbox)
    description = await get_openai_api_response(data=context_data, chat=chat)
    await repo.save_question_answer(question=chat.text, answer=description)
    return {"description": description}
