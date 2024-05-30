from fastapi import FastAPI, Depends, HTTPException
from sqlmodel import Session, select
from typing import Annotated
from contextlib import asynccontextmanager
from typing import AsyncGenerator
from jose import jwt, JWTError
from datetime import datetime, timedelta
from fastapi.security import OAuth2PasswordRequestForm, OAuth2PasswordBearer

from todo_practice.db import create_tables, get_session
from todo_practice.models import Todo
from todo_practice.route.user import user_router


# Step-7: Create contex manager for app lifespan
@asynccontextmanager   # Allows you to run setup code before the application starts and teardown code after the application shuts down. 
async def lifespan(app:FastAPI) -> AsyncGenerator[None,None]:   # indicates that the lifespan function is an async generator(type hint is used to indicate that a function returns an asynchronous generator) that doesn't produce any values (the first None) and doesn't accept any values sent to it (the second None)
    print("Creating Tables")
    create_tables()
    print("Tables Created")
    yield     # Control is given back to FastAPI, app starts here. code before yield will run before the startup and code after the yield statement runs after the application shuts down
    print("App is shutting down")

# Create instance of FastAPI class 
app : FastAPI = FastAPI(
    lifespan=lifespan, # lifespan tells FastAPI to use the lifespan function to manage the application's lifespan events
    title="My Todos", 
    version="1.0",
    servers=[
        {
            "url": "http://127.0.0.1:8000",
            "description": "Development Server"
        }
    ]
    ) 

# include user route in app to run from here
app.include_router(router=user_router)


# Step-9: Create all endpoints of todo app
@app.get("/")
async def root():
    return {"Hello" : "This is daily Do Todo app."}


@app.post("/todo", response_model=Todo)  # response will be validated by Todo schema
# users can create todos using Todo class schema and get session function (provided as dependancy injection(session depends on get_session)). 
async def create_todo(todo: Todo, session: Annotated[Session,Depends(get_session)]) -> Todo:   # Annotated used to create custom type.
    session.add(todo)
    session.commit()
    session.refresh(todo)
    return todo

@app.get("/todos", response_model=list[Todo]) # List of Todos will be returned.
async def get_all(session:Annotated[Session, Depends(get_session)]):
    # SQLModel queries: Select all Todos and execute all
    statement = select(Todo)
    todos = session.exec(statement).all()
    if todos:
        return todos
    else:
        raise HTTPException(status_code=404, detail="No Task Found")

@app.get("/todos/{id}", response_model=Todo )
async def get_one(id: int ,session:Annotated[Session, Depends(get_session)]):
    # SQLModel queries: Select Todo of given id and execute first result
    statement = select(Todo).where(Todo.id == id)
    todo = session.exec(statement).first()
    if todo:
        return todo
    else:
        raise HTTPException(status_code=404, detail="No Task Found")

@app.put("/todos/{id}", response_model=Todo )
async def edit_one(id: int, edited_todo_by_user:Todo, session:Annotated[Session, Depends(get_session)]):
    # SQLModel queries: Select Todo of given id and execute first result
    statement = select(Todo).where(Todo.id == id)
    todo_for_edit = session.exec(statement).first()
    if todo_for_edit:
        todo_for_edit.content = edited_todo_by_user.content    #edited_todo_by_user.content coming from function parameter which user will input
        todo_for_edit.is_completed = edited_todo_by_user.is_completed    #edited_todo_by_user..is_completed coming from function parameter which user will input
        # for posting new edited todo 
        session.add(todo_for_edit)
        session.commit()
        session.refresh(todo_for_edit) # to return from database
        return todo_for_edit
    else:
        raise HTTPException(status_code=404, detail="No Task Found")
    
@app.delete("/todos{id}")
async def delete_todo(id: int, session:Annotated[Session, Depends(get_session)]):
    statement = select(Todo).where(Todo.id == id)
    todo_to_delete = session.exec(statement).first()
    if todo_to_delete:
        session.delete(todo_to_delete)
        session.commit()
        return {"message": "Task Deleted Successfully"}
    else:
        raise HTTPException(status_code=404, detail="No Task Found")































# Creating Access Token to give to user for authorisation 
ALGORITHM: str = "HS256"  # Defining the algorithm used for JWT encoding
SECRET_KEY: str = "A Secret Key"  # Defining the secret key for encoding and decoding JWTs

def create_access_token(subject: str, expires_delta: timedelta):  # Function to create a JWT access token
    expire = datetime.utcnow() + expires_delta  # Setting the token expiry time
    to_encode = {"exp": expire, "sub": str(subject)}  # Creating the payload with expiry time and subject
    encode_jwt = jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)  # Encoding the payload to create JWT
    return encode_jwt  # Returning the generated JWT

@app.get("/get-token")  # Defining a GET endpoint to generate an access token
async def get_access_token(name: str):  # Asynchronous function to handle the token generation request
    token_expiry = timedelta(minutes=1)  # Setting the token expiry time to 1 minute
    print("Access Token Expiry Time", token_expiry)  # Printing the token expiry time to the console
    generated_token = create_access_token(subject=name, expires_delta=token_expiry)  # Creating the access token
    return {"Access Token": generated_token}  # Returning the generated token in a JSON response

def decode_access_token(token: str):  # Function to decode a JWT access token
    decoded_jwt = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])  # Decoding the JWT using the secret key and algorithm
    return decoded_jwt  # Returning the decoded JWT payload

@app.get("/decode-token")  # Defining a GET endpoint to decode an access token
async def decode_token(token: str):  # Asynchronous function to handle the token decoding request
    try:  # Trying to decode the token
        decoded_data = decode_access_token(token)  # Decoding the access token
        return decoded_data  # Returning the decoded data in a JSON response
    except JWTError as e:  # Handling JWT errors
        return {"error": str(e)}  # Returning the error message in a JSON response


fake_users_db: dict[str, dict[str, str]] = {
    "ameenalam": {
        "username": "ameenalam",
        "full_name": "Ameen Alam",
        "email": "ameenalam@example.com",
        "password": "ameenalamsecret",
    },
    "mjunaid": {
        "username": "mjunaid",
        "full_name": "Muhammad Junaid",
        "email": "mjunaid@example.com",
        "password": "mjunaidsecret",
    },
}

@app.post("/login")  # Defining a POST endpoint for user login
async def login_request(data_from_user: Annotated[OAuth2PasswordRequestForm, Depends(OAuth2PasswordRequestForm)]):  # Asynchronous function to handle the login request, using OAuth2PasswordRequestForm for user credentials
    
    # Step 1 : Validate user credentials from DB
    user_in_db = fake_users_db.get(data_from_user.username)  # Checking if the username exists in the fake database
    if user_in_db is None:  # If username is not found
        raise HTTPException(status_code=400, detail="Incorrect username")  # Raise an HTTP exception with status code 400 and error message

    # Step 2 : Validate password from DB
    if user_in_db["password"] != data_from_user.password:  # Checking if the provided password matches the stored password
        raise HTTPException(status_code=400, detail="Incorrect password")  # Raise an HTTP exception with status code 400 and error message
    
    # Step 3 : Create access token
    token_expiry = timedelta(minutes=1)  # Setting the token expiry time to 1 minute
    generated_token = create_access_token(subject=data_from_user.username, expires_delta=token_expiry)  # Creating the access token using the provided username and expiry time

    return {"username": data_from_user.username, "access_token": generated_token}  # Returning the username and generated access token in a JSON response


# Authentication using OAuth2PasswordBearer
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="login")  # Defining the OAuth2PasswordBearer scheme with the token URL pointing to the login endpoint

@app.get("/special-item")  # Defining a GET endpoint to access a special item
async def special_item(token: Annotated[str, Depends(oauth2_scheme)]):  # Asynchronous function to handle the request, extracting the token using the OAuth2PasswordBearer scheme
    decoded_data = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])  # Decoding the JWT token to retrieve the payload using the secret key and algorithm
    return {"username": token, "decoded data": decoded_data}  # Returning the token and the decoded data in a JSON response




