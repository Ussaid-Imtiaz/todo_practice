# Use an official Python runtime as a parent image
FROM python:3.12-slim

# maintainer of the file
LABEL maintainer="imtiazussaid@gmail.com"

# cd into /code
WORKDIR /code

# Copy the current directory files into the container at /code
COPY . /code

# Install poetry
RUN pip install poetry
# Configuration to avoid creating virtual environments inside the Docker container
RUN poetry config virtualenvs.create false
# install dependencies with poetry
RUN poetry install

# Make port 8000 available to the world outside this container
EXPOSE 8000

# Run the app. CMD can be overridden when starting the container
CMD [ "poetry", "run", "uvicorn", "todo_practice.main:app", "--host", "0.0.0.0", "--reload" ]


