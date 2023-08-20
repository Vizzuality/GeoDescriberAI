import datetime
from typing import Annotated

import jwt
from fastapi import Depends
from fastapi.security import OAuth2PasswordBearer

from config.config import get_config

# from database.db_config import secret

secret = get_config().secret

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="login")


def create_token(username: str):
    expiration_time = datetime.datetime.utcnow() + datetime.timedelta(days=1)
    payload = {
        "username": username,
        "exp": expiration_time,
    }
    return jwt.encode(payload, secret, algorithm="HS256")


def decode_token(token: str):
    return jwt.decode(token, secret, algorithms=["HS256"])


async def get_current_user(token: Annotated[str, Depends(oauth2_scheme)]):
    username = decode_token(token)
    print('** DECODED TOKEN **')
    return username
