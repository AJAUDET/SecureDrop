# syntax=docker/dockerfile:1

# Comments are provided throughout this file to help you get started.
# If you need more help, visit the Dockerfile reference guide at
# https://docs.docker.com/go/dockerfile-reference/

# Want to help us make this template better? Share your feedback here: https://forms.gle/ybq9Krt8jtBL3iCk7

# user/Dockerfile
FROM python:3.11-slim
WORKDIR /app

# Install dependencies
COPY user/requirements.txt .
RUN pip install -r requirements.txt

# Copy app code
COPY user/ .

# Inject environment variables
ENV USER_ID=""
ENV USER_NAME=""
ENV BACKEND_URL="http://securedrop-backend:8080"

CMD ["python", "securedrop.py"]