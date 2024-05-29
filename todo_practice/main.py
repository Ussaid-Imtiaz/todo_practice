from fastapi import FastAPI, Depends, HTTPException
from sqlmodel import SQLModel, Field, create_engine, Session, select
from todo_practice import setting
from typing import Annotated
from contextlib import asynccontextmanager
from typing import AsyncGenerator
from jose import jwt, JWTError
from datetime import datetime, timedelta
from fastapi.security import OAuth2PasswordRequestForm

# Step-1: Create Database on Neon
# Step-2: Create .env file for environment variables
# Step-3: Create setting.py file for encrypting DatabaseURL

# Create a variable using url as parameter and add psycopg with postgresql in url.
connection_string: str = str(   # Convert URL into string
    setting.DATABASE_URL
    ).replace(      
    "postgresql", 
    "postgresql+psycopg"
    )         

# Step-4: Create engine using sqlmodel to create connection between SQLModel and Postgresql
engine = create_engine( 
    connection_string, 
    # connect_args={"sslmode": "require"}, # use ssl(secure socket layer) to encrypt communication with DB.
    pool_recycle=300, # SQL engine use pool of connections to minimise time of each request, recycle upto 5 mins (300seconds)
    pool_size=10, 
    echo=True
    )  


# Step-5: Create function for table creation. 
def create_tables() -> None:
    SQLModel.metadata.create_all(engine)    # Contents of Schema (with tables) is registered with metadata attribute of sqlmodel

# Step-6: Create function for session management 
def get_session():
    with Session(engine) as session:        # With will auto close session.
        yield session                       # yield (generator function) will iterate over sessions.

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

# Step-8: Create model class using tables to use as schema in APIs 
class Todo(SQLModel, table = True):
    id : int | None = Field(primary_key=True, default = None)
    content: str = Field(index = True, min_length=3, max_length=54)
    is_completed : bool = Field(default=False)


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
ALGORITHM: str = "HS256"
SECRET_KEY: str = "A Secret Key"

def create_access_token(subject: str, expires_delta: timedelta):
    expire = datetime.utcnow() + expires_delta
    to_encode = {"exp": expire, "sub": str(subject)}
    encode_jwt = jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)
    return encode_jwt

@app.get("/get-token")
async def get_access_token(name: str):
    token_expiry = timedelta(minutes=1)
    print("Access Token Expiry Time", token_expiry)
    generated_token = create_access_token(subject=name, expires_delta=token_expiry)
    return {"Access Token": generated_token}

def decode_access_token(token:str):
    decoded_jwt = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
    return decoded_jwt

@app.get("/decode-token")
async def decode_token(token:str):
    try:
        decoded_data = decode_access_token(token)
        return decoded_data
    except JWTError as e:
        return {"error": str(e)}


@app.post("/login")
async def login_request(data_from_user: Annotated[OAuth2PasswordRequestForm, Depends(OAuth2PasswordRequestForm)]):
    return {"username": data_from_user.username, "password": data_from_user.password}
