FROM python:3.10.8

WORKDIR /app
COPY . .

RUN pip install -r requirements.txt

CMD uvicorn --host=127.0.0.1 --port=8080 --factory api.api:create_app