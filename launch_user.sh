#!/bin/bash

NETWORK_NAME="securedrop_lan"

# Check if network exists
if ! docker network inspect $NETWORK_NAME >/dev/null 2>&1; then
  echo "Creating network $NETWORK_NAME"
  docker network create -d macvlan \
    --subnet=192.168.1.0/24 \
    --gateway=192.168.1.1 \
    -o parent=eth0 \
    $NETWORK_NAME
fi

# Usage: ./launch_user.sh <username> <email> <password>
if [ $# -ne 3 ]; then
  echo "Usage: $0 <username> <email> <password>"
  exit 1
fi

USER=$1
EMAIL=$2
PASSWORD=$3
VOLUME="${USER}_data"
CONTAINER_NAME="${USER}_container"
IMAGE_NAME="securedrop_user_container:latest"

# -------------------------------
# 1. Build the Docker image if it doesn't exist
if ! docker image inspect $IMAGE_NAME >/dev/null 2>&1; then
  echo "Building Docker image: $IMAGE_NAME"
  docker-compose build
fi

# -------------------------------
# 2. Create a Docker volume for the user if missing
if ! docker volume inspect $VOLUME >/dev/null 2>&1; then
  echo "Creating Docker volume: $VOLUME"
  docker volume create $VOLUME
fi

# -------------------------------
# 3. Remove existing container if present
if docker ps -a --format '{{.Names}}' | grep -Eq "^${CONTAINER_NAME}$"; then
  echo "Removing existing container: $CONTAINER_NAME"
  docker rm -f $CONTAINER_NAME
fi

# -------------------------------
# 4. Launch the container with environment variables
docker run -it \
  --name $CONTAINER_NAME \
  -e USER_NAME=$USER \
  -e USER_EMAIL=$EMAIL \
  -e USER_PASSWORD=$PASSWORD \
  -v $VOLUME:/app/data \
  --network securedrop_lan \
  $IMAGE_NAME \
  bash

echo "✅ Container '$CONTAINER_NAME' launched with volume '$VOLUME'"