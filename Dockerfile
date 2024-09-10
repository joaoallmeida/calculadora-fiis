FROM python:3.10.12-slim

# Configure Poetry
ENV POETRY_HOME=/opt/poetry
ENV POETRY_VENV=/opt/poetry-venv
ENV POETRY_CACHE_DIR=/opt/.cache
ENV PATH="${PATH}:${POETRY_VENV}/bin"

RUN apt-get update
RUN apt-get install -y --no-install-recommends \
                        libatlas-base-dev \
                        python3-dev \
                        build-essential \ 
                        libssl-dev \
                        libffi-dev

WORKDIR /app
COPY /app /app
COPY pyproject.toml .

RUN pip install --upgrade pip setuptools wheel && pip install poetry
RUN poetry install


EXPOSE 5000
CMD ["uwsgi", "--ini", "./wsgi.ini"]