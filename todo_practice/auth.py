from typing import Annotated
from fastapi import Depends
from passlib.context import CryptContext
from sqlmodel import Session, select

from todo_practice.db import get_session
from todo_practice.models import User

pwd_context = CryptContext(schemes="bcrypt")

def hash_pwd(password):
    return pwd_context.hash(password)

def get_user_from_db(session: Annotated[Session, Depends(get_session)], username:str, email:str):
    statement = select(User).where(User.username == username)
    user_found = session.exec(statement).first()
    if not user_found:
        statement = select(User).where(User.email == email)
        user_found = session.exec(statement).first()
        return user_found
    return user_found
