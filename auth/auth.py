import datetime
import os

import jwt

SECRET_KEY = os.getenv("SECRET_KEY")  # Make sure to keep this secret and secure


def create_token(user_id: str):
    expiration_time = datetime.datetime.utcnow() + datetime.timedelta(days=1)
    payload = {
        "user_id": user_id,
        "exp": expiration_time,
    }
    return jwt.encode(payload, SECRET_KEY, algorithm="HS256")


def decode_token(token: str):
    return jwt.decode(token, SECRET_KEY, algorithms=["HS256"])
