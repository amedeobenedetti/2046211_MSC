FROM python:3.11

WORKDIR /app

COPY . .

RUN pip install fastapi pydantic pika requests sqlalchemy psycopg2-binary

CMD ["python", "main.py"]