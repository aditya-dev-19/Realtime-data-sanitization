FROM python:3.11-slim

WORKDIR /app

# Install system deps
RUN apt-get update && apt-get install -y \
    gcc libpq-dev git curl \
    && rm -rf /var/lib/apt/lists/*

# Copy requirements and install
# [MODIFIED] Removed 'backend/' from the path
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Install spaCy English model
RUN python -m spacy download en_core_web_sm

# Copy project code + models
# [MODIFIED] Removed 'backend/' from the paths
COPY api/ /app/api/
COPY models/ /app/models/
COPY saved_models/ /app/saved_models/

# Expose Cloud Run port
EXPOSE 8080

# Create database tables and run migrations
WORKDIR /app/api
RUN python -c "from database import init_db; init_db()"

# Run FastAPI
CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8080"]