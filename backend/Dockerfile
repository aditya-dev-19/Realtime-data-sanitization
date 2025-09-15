FROM python:3.11-slim

WORKDIR /app

# Install system deps
RUN apt-get update && apt-get install -y \
    gcc libpq-dev git curl \
    && rm -rf /var/lib/apt/lists/*

# Copy requirements and install
COPY backend/requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Install spaCy English model
RUN python -m spacy download en_core_web_sm

# Copy project code + models
COPY backend/api/ /app/api/
COPY backend/models/ /app/models/
COPY backend/saved_models/ /app/saved_models/

# Expose Cloud Run port
EXPOSE 8080

# Run FastAPI
WORKDIR /app/api
CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8080"]
