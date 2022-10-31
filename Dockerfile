FROM python:3.9

COPY . /home
WORKDIR /home
RUN pip install poetry==1.1.14 && poetry install

CMD [ "python", "./app.py" ]
