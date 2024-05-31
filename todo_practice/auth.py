from typing import Annotated
from fastapi import Depends
from fastapi.security import OAuth2PasswordBearer
from passlib.context import CryptContext
from sqlmodel import Session, select
from jose import jwt, JWTError
from datetime import timedelta, datetime, timezone

from todo_practice.db import get_session
from todo_practice.models import User

pwd_context = CryptContext(schemes="bcrypt")
def hash_pwd(password):
    return pwd_context.hash(password)
def verify_pwd(password, hash_password):
    return pwd_context.verify(password, hash_password)

def get_user_from_db(session: Annotated[Session, Depends(get_session)],
                     username: str | None = None,
                     email: str | None = None):
    statement = select(User).where(User.username == username)
    user = session.exec(statement).first()
    print(user)
    if not user:
        statement = select(User).where(User.email == email)
        user = session.exec(statement).first()
        if user:
            return user

    return user


oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/token")

def authenticate_user(username,
                      password,
                      session: Annotated[Session, Depends(get_session)]):
    db_user = get_user_from_db(session=session, username=username)
    print(f""" authenticate {db_user} """)
    if not db_user:
        return False
    if not verify_pwd(password, db_user.password):
        return False
    return db_user

SECRET_KEY = "A very Secret Key"
ALGORITHM = "HS256"
EXPIRY_TIME = 30

def create_access_token(data: dict, expiry_time: timedelta | None ):
    data_to_encode = data.copy()
    if expiry_time:
        expire = datetime.now(timezone.utc) + expiry_time
    else:
        expire = datetime.now(timezone.utc) + timedelta(minutes=15)
    data_to_encode.update({"exp":expire}) 

    encoded_jwt = jwt.encode(data_to_encode, SECRET_KEY, algorithm=ALGORITHM)

    return encoded_jwt
    