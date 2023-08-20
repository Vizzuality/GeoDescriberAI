from fastapi import FastAPI, HTTPException
from fastapi.params import Depends
from pydantic import BaseModel

from auth.auth import create_token
from database.repository import get_mongo_repository
from processing.context_data import get_overpass_api_response
from processing.description import get_openai_api_response
from questions_answers.repository import QuestionAnswerRepository, get_qa_repository
from users.repository import UserRepository, get_user_repository

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


@app.post("/login")
async def login(username: str, password: str, user_repo: UserRepository = Depends(get_user_repository)):
    user = await user_repo.get_user_by_credentials(username, password)
    if user:
        token = create_token(user.id)
        return {"access_token": token}
    else:
        raise HTTPException(status_code=401, detail="Invalid credentials")


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
