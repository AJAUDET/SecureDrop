# --- Base Image ---
FROM python:3.12-slim

# --- Environment Variables ---
ENV PYTHONUNBUFFERED=1 \
    PIP_NO_CACHE_DIR=1

# --- Install system dependencies ---
RUN apt-get update && \
    apt-get install -y --no-install-recommends \
        build-essential \
        libssl-dev \
        libffi-dev \
        python3-dev \
        git \
        nano \
        iputils-ping \
        net-tools \
        curl && \
    rm -rf /var/lib/apt/lists/*

# --- Set working directory ---
WORKDIR /app

# --- Copy source code ---
COPY . /app

# --- Install Python dependencies ---
RUN pip install --upgrade pip
RUN if [ -f requirements.txt ]; then pip install -r requirements.txt; fi

# --- Ensure templates directory exists ---
RUN mkdir -p /app/templates

# --- Create default template files ---
# (these will be copied to user volumes on first run)
COPY templates/ /app/templates/

# --- Set default command ---
CMD ["python3", "securedrop.py"]