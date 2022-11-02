FROM python:3-slim as python
ENV PYTHONUNBUFFERED=true
ARG API_ID
ARG API_HASH
ARG BOT_TOKEN

ENV POETRY_VERSION=1.2.0
ENV POETRY_HOME=/opt/poetry
ENV POETRY_VENV=/opt/poetry-venv
ENV POETRY_CACHE_DIR=/opt/.cache

RUN python3 -m venv $POETRY_VENV \
    && $POETRY_VENV/bin/pip install -U pip setuptools \
    && $POETRY_VENV/bin/pip install poetry==${POETRY_VERSION}

ENV PATH="${PATH}:${POETRY_VENV}/bin"

WORKDIR /app

COPY poetry.lock pyproject.toml ./
RUN poetry install

COPY . /app
RUN echo -e "BOT_TOKEN = $BOT_TOKEN\nAPI_ID = $API_ID\nAPI_HASH = $API_HASH" > ".env"

EXPOSE 8080
CMD [ "poetry", "run", "python", "app.py" ]
