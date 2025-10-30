FROM python:3.12-slim

WORKDIR /app

# Copy application code only
COPY securedrop.py user.py verify.py contactmanage.py password.py network.py welcome.py /app/

# Ensure /app/data exists for per-user volumes
RUN mkdir -p /app/data

# Install required packages
RUN pip install pycryptodome pwinput

# Default entrypoint
ENTRYPOINT ["python3", "securedrop.py"]