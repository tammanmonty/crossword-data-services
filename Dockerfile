# Use Python 3.10 slim image as base (smaller size, fewer packages)
FROM python:3.10-slim

# Metadata: specifies the author of this Docker image
LABEL authors="Tamman Montanaro"

# Prevent Python from writing .pyc files to disk (reduces image size)
ENV PYTHONDONTWRITEBYTECODE=1

# Force Python output to be sent straight to terminal without buffering
# This ensures logs are immediately visible in Docker logs
ENV PYTHONUNBUFFERED=1

# Set the working directory inside the container
WORKDIR /data_pipeline

# Copy requirements file first (leverages Docker layer caching)
# If requirements.txt hasn't changed, this layer will be cached
COPY requirements.txt .

# Install Python dependencies without caching pip downloads (saves space)
RUN pip install --no-cache-dir -r requirements.txt

# Copy the application code to the container
# This copies from host's /data_pipeline directory to container's /data_pipeline directory
COPY /data_pipeline /data_pipeline

# Define the command to run when container starts
# Runs the main.py module from the app package
CMD ["python", "-m", "data_pipeline.main"]