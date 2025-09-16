# Use an updated Python runtime as a parent image
FROM python:3.11-slim

# Set the working directory in the container
WORKDIR /app

# Copy the requirements file into the container at /app
COPY requirements.txt .

# Install any needed packages specified in requirements.txt
RUN pip install --no-cache-dir -r requirements.txt

# Copy the rest of the application's code into the container
COPY ./api /app/api
COPY ./models /app/models

# Expose the port the app runs on (this is for documentation)
EXPOSE 8080

# [MODIFIED] Run main.py using the $PORT environment variable
CMD ["uvicorn", "api.main:app", "--host", "0.0.0.0", "--port", "$PORT"]