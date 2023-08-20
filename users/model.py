from typing import Optional

from pydantic import BaseModel


class User(BaseModel):
    username: str
    password: str
    full_name: Optional[str] = None
    email: Optional[str] = None
