# Backend Dockerfile - Python Flask app
FROM python:3.11-slim

WORKDIR /app

# Install build deps
RUN apt-get update && apt-get install -y --no-install-recommends \
    build-essential \
    && rm -rf /var/lib/apt/lists/*

# Copy requirements and install
COPY requirements.txt ./
RUN pip install --no-cache-dir -r requirements.txt

# Copy app source
COPY . /app

ENV PYTHONUNBUFFERED=1

EXPOSE 5000

# Use gunicorn for production-ish server; fallback to python app.py if not present
CMD ["sh", "-c", "gunicorn -b 0.0.0.0:5000 app:app --workers 1 || python app.py"]
