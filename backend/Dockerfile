# Use an official Python runtime as a parent image
FROM python:3.9-slim

# Set the working directory in the container
WORKDIR /app

# Copy the requirements file into the container at /app
COPY requirements.txt .

# Install any needed packages specified in requirements.txt
# Make sure 'google-cloud-storage' is listed in your requirements.txt
RUN pip install --no-cache-dir -r requirements.txt

# Copy the rest of the application's code into the container
# This includes your 'api' and 'models' directories, but NOT the old 'saved_models'
COPY ./api /app/api
COPY ./models /app/models

# Expose the port the app runs on
EXPOSE 8000

# Run main.py when the container launches
# Use uvicorn to run the FastAPI application
CMD ["uvicorn", "api.main:app", "--host", "0.0.0.0", "--port", "8000"]