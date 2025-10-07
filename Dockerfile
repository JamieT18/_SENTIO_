# Sentio API Dockerfile
FROM python:3.12-slim

WORKDIR /app

COPY requirements.txt requirements.txt
COPY requirements-api.txt requirements-api.txt
RUN pip install --no-cache-dir -r requirements.txt -r requirements-api.txt

COPY sentio/ sentio/
COPY dashboard/ dashboard/
COPY examples/ examples/
COPY tools/ tools/
COPY setup.py setup.py

EXPOSE 8000

CMD ["uvicorn", "sentio.api.main:app", "--host", "0.0.0.0", "--port", "8000"]
