FROM python:3.11-slim

WORKDIR /app

RUN apt-get update && apt-get install -y \
    gcc \
    g++ \
    make \
    graphviz \
    libgraphviz-dev \
    pkg-config \
    postgresql-client \
    && rm -rf /var/lib/apt/lists/*

COPY requirements.txt .
RUN pip install --no-cache-dir --upgrade pip
RUN pip install --no-cache-dir -r requirements.txt

COPY . .

ENV PYTHONUNBUFFERED=1

CMD ["sh", "-c", "\
    until pg_isready -h db -p 5432; do \
        echo 'Waiting for database...'; \
        sleep 2; \
    done; \
    alembic upgrade head && \
    uvicorn app.main:app --host 0.0.0.0 --port 8000"]
