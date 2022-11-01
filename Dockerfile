FROM python:3-slim as python
ENV PYTHONUNBUFFERED=true
ARG API_ID
ARG API_HASH
ARG BOT_TOKEN

WORKDIR /app

FROM python as poetry
ENV POETRY_HOME=/opt/poetry
ENV POETRY_VIRTUALENVS_IN_PROJECT=true
ENV PATH="$POETRY_HOME/bin:$PATH"
RUN python -c 'from urllib.request import urlopen; print(urlopen("https://install.python-poetry.org").read().decode())' | python -
COPY . ./
RUN poetry install --no-interaction --no-ansi -vvv


FROM python as runtime
ENV PATH="/app/.venv/bin:$PATH"
COPY --from=poetry /app /app

RUN echo -e "BOT_TOKEN = ${BOT_TOKEN}\nAPI_ID = ${API_ID}\nAPI_HASH = ${API_HASH}" > ".env"
EXPOSE 8080
CMD [ "poetry", "run", "./app.py" ]
