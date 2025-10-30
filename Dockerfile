# SecureDrop Dockerfile

FROM python:3.11-slim

# Set working directory
WORKDIR /app

# Copy requirements first (for caching)
COPY requirements.txt .

# Install dependencies
RUN pip install --no-cache-dir -r requirements.txt

# Copy the rest of the source code
COPY . .

# Ensure data directory exists
RUN mkdir -p /app/data

# Default command - can be overridden by docker-compose
CMD ["python3", "securedrop.py"]