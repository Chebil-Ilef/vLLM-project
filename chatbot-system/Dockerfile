FROM python:3.11-slim

WORKDIR /app

RUN apt-get update && apt-get install -y --no-install-recommends \
    build-essential \
    ca-certificates \
    git \
    wget \
    && rm -rf /var/lib/apt/lists/*

COPY requirements.txt ./
RUN pip install --no-cache-dir -r requirements.txt || true

COPY . /app

ENV PYTHONUNBUFFERED=1

EXPOSE 5000

# Make startup script executable
RUN chmod +x wait-for-services.py

CMD ["sh", "-c", "python wait-for-services.py && gunicorn -b 0.0.0.0:5000 app:app --workers 1 || python app.py"]
