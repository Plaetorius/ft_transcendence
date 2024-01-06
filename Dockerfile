# Latest version of Python
FROM python:3.10

# Not critical data
ENV PYTHONDONTWRITEBYTECODE 1
ENV PYTHONUNBUFFERED 1

# Install Pipenv; done in Docker to encapsulate dependencies for better portability
RUN pip install pipenv 
# django psycopg2-binary

WORKDIR /code

# Install dependencies
COPY Pipfile Pipfile.lock* /code/
RUN pipenv install --deploy --system

# Generate Pipfile.lock
# RUN pipenv lock

# Copy project
COPY src/ /code/
