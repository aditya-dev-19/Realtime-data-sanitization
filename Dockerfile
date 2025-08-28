# Use an official Python runtime as a base image
FROM python:3.11-slim

# Set the working directory inside the container
WORKDIR /app

# Copy the requirements file first to leverage Docker's layer caching
COPY requirements.txt .

# Increase the timeout for pip to handle slow connections
RUN pip install --default-timeout=600 --no-cache-dir -r requirements.txt
RUN python -m spacy download en_core_web_sm

# Copy your entire project into the container
COPY . /app/

# Tell Docker that your application listens on port 8000
EXPOSE 8000

# The command to run when the container starts
CMD ["uvicorn", "api.main:app", "--host", "0.0.0.0", "--port", "8000"]