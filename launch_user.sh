#!/bin/bash
# launch_user.sh
# Usage:
#   ./launch_user.sh                 -> interactive login/register
#   ./launch_user.sh <username>      -> login with username
#   ./launch_user.sh <username> <password> -> login with username and password

# Configuration
IMAGE_NAME="securedrop-docker_user_container"
AUTH_VOLUME="securedrop_auth"
DATA_VOLUME="securedrop_data"

# Ensure volumes exist
docker volume create $AUTH_VOLUME > /dev/null
docker volume create $DATA_VOLUME > /dev/null

# Get arguments
USERNAME="$1"
PASSWORD="$2"

# Determine environment variables for the container
ENV_VARS=""
if [ -n "$USERNAME" ]; then
    ENV_VARS="-e USER_NAME=$USERNAME"
fi
if [ -n "$PASSWORD" ]; then
    ENV_VARS="$ENV_VARS -e USER_PASSWORD=$PASSWORD"
fi

# Generate container name (avoid conflicts)
CONTAINER_NAME="${USERNAME:-securedrop}_container"

# Remove existing container with same name
if [ "$(docker ps -aq -f name=$CONTAINER_NAME)" ]; then
    echo "[INFO] Removing existing container $CONTAINER_NAME..."
    docker rm -f $CONTAINER_NAME
fi

echo "[INFO] Launching container $CONTAINER_NAME..."

docker run -it \
    --name "$CONTAINER_NAME" \
    $ENV_VARS \
    -v "$AUTH_VOLUME:/app/auth" \
    -v "$DATA_VOLUME:/app/data" \
    "$IMAGE_NAME" \
    bash