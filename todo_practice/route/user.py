from fastapi import APIRouter, Depends, HTTPException
from typing import Annotated
from sqlmodel import Session
from todo_practice.db import get_session
from todo_practice.models import Register_User, User
from todo_practice.auth import get_user_from_db, hash_pwd
from fastapi.security import OAuth2PasswordBearer


user_router = APIRouter(
    prefix="/user",
    tags=["user"],
    responses={404: {"description": "Not Found"} }
)

@user_router.get("/")
async def root():
    return {"message": "Wellcome to Users Page"}

# Register User by checking if user already exists in database
@user_router.post("/register")
async def register_user(new_user: Annotated[Register_User, Depends()], session: Annotated[Session, Depends(get_session)]):

    db_user = get_user_from_db(session, new_user.username, new_user.email)
    if db_user:
        raise HTTPException(status_code = 409, detail="User with these credential already exists")
    
    user = User(username = new_user.username, email = new_user.email, password = hash_pwd(new_user.password))

    session.add(user)
    session.commit()
    session.refresh(user)
    
    return {"message": f""" User with {user.username} successfully registered"""}


# @user_router.get("/me")
# async def user_profile(current_user: Annotated[User, Depends(oauth2_scheme)]):
#     return {"message": "Hello World"}





