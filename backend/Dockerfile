
FROM python:3.11-slim

WORKDIR /app

COPY requirements.txt .
RUN pip install -r requirements.txt

COPY . .

ENV PYTHONUNBUFFERED=1

CMD alembic upgrade head && uvicorn app.main:app --host 0.0.0.0 --port 8000