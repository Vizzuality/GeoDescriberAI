from typing import Annotated

from fastapi import FastAPI, Depends, HTTPException
from fastapi.security import OAuth2PasswordRequestForm
from pydantic import BaseModel

from auth.auth import create_token, get_current_user
from database.repository import get_mongo_repository
from processing.context_data import get_overpass_api_response
from processing.description import get_openai_api_response
from questions_answers.repository import get_qa_repository, QuestionAnswerRepository
from users.repository import get_user_repository, UserRepository

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
async def login(form_data: Annotated[OAuth2PasswordRequestForm, Depends()],
                user_repo: UserRepository = Depends(get_user_repository, use_cache=True)):
    username, password = form_data.username, form_data.password
    user = await user_repo.get_user_by_credentials(username, password)
    print('***** USER *******', user)
    print('***** USERNAME *******', username)
    print("*** PASSWORD ***", password)
    if user:
        token = create_token(username)
        return {"access_token": token}
    else:
        raise HTTPException(status_code=401, detail="Invalid credentials")


@app.post("/context")
async def get_context_data(bbox: Bbox):
    context_data = await get_overpass_api_response(bbox)
    return context_data


@app.post("/description", tags=["Protected"])
async def get_description(bbox: Bbox, chat: Chat,
                          repo: QuestionAnswerRepository = Depends(get_qa_repository, use_cache=True),
                          current_user: str = Depends(get_current_user)):
    context_data = await get_overpass_api_response(bbox)
    description = await get_openai_api_response(data=context_data, chat=chat)
    await repo.save_question_answer({"username": current_user, "question": chat.text, "answer": description})
    return {"description": description}
