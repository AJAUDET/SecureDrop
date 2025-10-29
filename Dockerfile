# Use a lightweight Python base image
FROM python:3.11-slim

# Prevent Python from writing .pyc files and buffering output
ENV PYTHONDONTWRITEBYTECODE=1
ENV PYTHONUNBUFFERED=1

# Set working directory
WORKDIR /app

# Install system dependencies (bash, nano, etc.) for debugging or development
RUN apt-get update && apt-get install -y --no-install-recommends \
    bash curl vim nano net-tools iputils-ping \
    && rm -rf /var/lib/apt/lists/*

# Copy only requirements first to leverage Docker layer caching
COPY requirements.txt .

# Install dependencies
RUN pip install --no-cache-dir -r requirements.txt

# Now copy the rest of the application
COPY . .

# Default command
CMD ["python3", "securedrop.py"]