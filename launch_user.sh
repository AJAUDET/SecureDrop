#!/bin/bash

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
IMAGE_NAME="securedrop-docker_user_container"  # Update if your image name differs

# Build image if not already built
docker-compose build

# Create Docker volume if missing
docker volume inspect $VOLUME >/dev/null 2>&1 || docker volume create $VOLUME

# Launch container with per-user volume and env variables
docker run -d \
  --name $CONTAINER_NAME \
  -e USER_NAME=$USER \
  -e USER_EMAIL=$EMAIL \
  -e USER_PASSWORD=$PASSWORD \
  -v $VOLUME:/app/data \
  --network securedrop_lan \
  $IMAGE_NAME

echo "Container for user '$USER' launched with volume '$VOLUME'"