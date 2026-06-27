FROM python:3.12-slim

WORKDIR /app

RUN apt-get update && apt-get install -y \
    build-essential \
    gcc \
    g++ \
    && rm -rf /var/lib/apt/lists/*

COPY backend/requirements.txt .

RUN pip install --upgrade pip
RUN pip install --default-timeout=1000 -r requirements.txt

COPY backend/ .
COPY frontend/ /frontend/

EXPOSE 5000

CMD ["python", "app.py"]