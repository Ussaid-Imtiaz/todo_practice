from pydantic import BaseModel
from sqlmodel import SQLModel, Field
from fastapi.security import OAuth2PasswordRequestForm
from fastapi import Form
from typing import Annotated


# Step-8: Create model class using tables to use as schema in APIs 
class Todo(SQLModel, table = True):
    id : int | None = Field(primary_key=True, default = None)
    content: str = Field(index = True, min_length=3, max_length=54)
    is_completed : bool = Field(default=False)
    user_id : int = Field(foreign_key="user.id")


class User(SQLModel, table=True):
    id:int | None = Field(primary_key=True, default=None)
    username: str
    email: str
    password: str

class Register_User(BaseModel):
    username: Annotated[str, Form()]
    email: Annotated[str, Form()]
    password: Annotated[str, Form()]



