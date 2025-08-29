FROM python:3.11-slim

# Set the working directory inside container
WORKDIR /app

# Install system dependencies (for some Python libs like SQLAlchemy, psycopg2, etc.)
RUN apt-get update && apt-get install -y \
    gcc \
    libpq-dev \
    && rm -rf /var/lib/apt/lists/*

# Copy requirements first (for layer caching)
COPY requirements.txt .

# Install dependencies
RUN pip install --no-cache-dir -r requirements.txt

# Copy the whole project (this brings in api/, saved_models/, etc.)
COPY . .

# Set working directory to api (since you run uvicorn from there)
WORKDIR /app/api

# Expose FastAPI port
EXPOSE 8080

# Run FastAPI (production mode)
CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8080"]
