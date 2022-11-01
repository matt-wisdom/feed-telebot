FROM python:3.9

ARG API_ID
ARG API_HASH
ARG BOT_TOKEN

COPY . /home
WORKDIR /home

RUN pip install poetry==1.1.14 && poetry install
RUN echo -e "BOT_TOKEN = ${BOT_TOKEN}\nAPI_ID = ${API_ID}\nAPI_HASH = ${API_HASH}" > ".env"

CMD [ "poetry", "run", "./app.py" ]
