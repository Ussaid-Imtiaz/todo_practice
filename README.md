## A Poetry Project Using FastAPI, Postgres Database, Docker, Kafka, Kong,

### Create New Poetry Project

poetry new daily_todo

make a file main.py

cd daily_todo

poetry add fastapi, sqlmodel, uvicorn, "pycopg[binary]", sqlmodel

### Use FastAPI

Write the code of FastAPI in main.py

Define different endpoints

Use authentication and authorisation (OAuth2)

### Create Database

Create Account on Neon Database

Create .env file for environment variables and copy URL from Neon and paste it here

Create setting.py file for encrypting DatabaseURL

### Use Docker

install and run docker desktop

Make a `Dockerfile.dev` file

(Optional) To Build image -> `docker build -f Dockerfile -t my-todo-image .`

(Optional) To Run the container -> `docker run -d --name todo-cont -p 8000:8000 my-todo-image`

Create `compose.yaml` file

Run `docker compose up -d` -> (detatch mode)

Use Dev Containers of VS Code

### Run in browser

`poetry run uvicorn todo_practice.main:app --host 127.0.0.1 --port 8000 --reload`
(-- reload for auto reload upon changes in code)
(-- host can also be localhost or 0.0.0.0)
(-- port can be any port upto 65000)

write [http://127.0.0.1:8000/docs] and click try it out. It will show what is in return statement
