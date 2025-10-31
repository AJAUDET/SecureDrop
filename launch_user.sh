#!/bin/bash
set -e

# Usage: ./launch_user.sh <username> <password> <email>
# Example: ./launch_user.sh host hostpass host@example.com

USERNAME="$1"
PASSWORD="$2"
EMAIL="$3"
IMAGE_NAME="securedrop-docker_user_container"
NETWORK_NAME="securedrop_bridge"

if [ -z "$USERNAME" ] || [ -z "$PASSWORD" ] || [ -z "$EMAIL" ]; then
    echo "Usage: $0 <username> <password> <email>"
    exit 1
fi

# Create Docker network if missing
if ! docker network ls | grep -q "$NETWORK_NAME"; then
    echo "[INFO] Creating network $NETWORK_NAME..."
    docker network create "$NETWORK_NAME"
fi

# Shared data directory (global for all containers)
SHARED_DATA="$(pwd)/shared_data"
mkdir -p "$SHARED_DATA"

# Per-user authentication directory
USER_AUTH="$(pwd)/users/$USERNAME/auth"
mkdir -p "$USER_AUTH"

# Per-user private data directory
USER_DATA="$(pwd)/users/$USERNAME/data"
mkdir -p "$USER_DATA"

CONTAINER_NAME="${USERNAME}_container"

# Remove old container if exists
if docker ps -a --format '{{.Names}}' | grep -q "^${CONTAINER_NAME}$"; then
    echo "[INFO] Removing existing container $CONTAINER_NAME..."
    docker rm -f "$CONTAINER_NAME"
fi

echo "[INFO] Launching SecureDrop container for user: $USERNAME"

docker run -it \
    --name "$CONTAINER_NAME" \
    --network "$NETWORK_NAME" \
    -v "$USER_AUTH:/app/auth" \
    -v "$SHARED_DATA:/app/data/shared" \
    -v "$USER_DATA:/app/data/private" \
    -e USER_NAME="$USERNAME" \
    -e USER_PASSWORD="$PASSWORD" \
    -e USER_EMAIL="$EMAIL" \
    "$IMAGE_NAME" \
    bash -c "python3 securedrop.py; cd /app/data/private; exec bash"

# Close out of container after use

if docker ps -a --format '{{.Names}}' | grep -q "^${CONTAINER_NAME}$"; then
    echo "[INFO] Removing existing container $CONTAINER_NAME..."
    docker rm -f "$CONTAINER_NAME"
fi