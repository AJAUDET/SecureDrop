#!/bin/bash
set -e

IMAGE_NAME="securedrop-docker_user_container"
USERNAME="$1"
PASSWORD="$2"
NETWORK_NAME="securedrop_bridge"

if [ -z "$USERNAME" ]; then
    echo "Usage: $0 <username> [password]"
    exit 1
fi

# User-specific directories on host
USER_DATA="./users/$USERNAME/data"
USER_AUTH="./users/$USERNAME/auth"

# Create folders if they don't exist
mkdir -p "$USER_DATA"
mkdir -p "$USER_AUTH"

CONTAINER_NAME="${USERNAME}_container"

# Remove container if it already exists
if docker ps -a --format '{{.Names}}' | grep -q "^${CONTAINER_NAME}$"; then
    echo "[INFO] Removing existing container ${CONTAINER_NAME}..."
    docker rm -f $CONTAINER_NAME
fi

echo "[INFO] Launching container for user: $USERNAME"

# Build docker run command interactively
RUN_CMD="docker run -it --name $CONTAINER_NAME --network $NETWORK_NAME \
    -v $USER_AUTH:/app/auth \
    -v $USER_DATA:/app/data \
    -e USER_NAME=\"$USERNAME\""

# Add password env if provided
if [ -n "$PASSWORD" ]; then
    RUN_CMD="$RUN_CMD -e USER_PASSWORD=\"$PASSWORD\""
fi

# Run securedrop.py, then drop into bash
RUN_CMD="$RUN_CMD $IMAGE_NAME bash -c 'python3 securedrop.py; exec bash'"

# Execute
eval $RUN_CMD