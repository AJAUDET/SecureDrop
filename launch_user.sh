set -e

IMAGE_NAME="securedrop-docker_user_container"
CONTAINER_NAME="${1:-interactive}_container"
USERNAME="$1"
PASSWORD="$2"
DATA_VOLUME="securedrop_data"
AUTH_VOLUME="securedrop_auth"
NETWORK_NAME="securedrop_bridge"

# Remove container if it already exists
if docker ps -a --format '{{.Names}}' | grep -q "^${CONTAINER_NAME}$"; then
    echo "[INFO] Removing existing container ${CONTAINER_NAME}..."
    docker rm -f $CONTAINER_NAME
fi

# Run the container
echo "[INFO] Launching container: $CONTAINER_NAME"

if [ -z "$USERNAME" ]; then
    # Interactive mode
    docker run -it \
        --name $CONTAINER_NAME \
        --network $NETWORK_NAME \
        -v ${AUTH_VOLUME}:/app/auth \
        -v ${DATA_VOLUME}:/app/data \
        $IMAGE_NAME
elif [ -n "$USERNAME" ] && [ -z "$PASSWORD" ]; then
    # Auto-login with username
    docker run -it \
        --name $CONTAINER_NAME \
        -e USER_NAME="$USERNAME" \
        --network $NETWORK_NAME \
        -v ${AUTH_VOLUME}:/app/auth \
        -v ${DATA_VOLUME}:/app/data \
        $IMAGE_NAME
else
    # Auto-login with username and password
    docker run -it \
        --name $CONTAINER_NAME \
        -e USER_NAME="$USERNAME" \
        -e USER_PASSWORD="$PASSWORD" \
        --network $NETWORK_NAME \
        -v ${AUTH_VOLUME}:/app/auth \
        -v ${DATA_VOLUME}:/app/data \
        $IMAGE_NAME
fi

# Optional: drop into bash shell after container exits
echo "[INFO] Container exited. Opening interactive shell..."
docker run -it --rm -v ${DATA_VOLUME}:/app/data -v ${AUTH_VOLUME}:/app/auth $IMAGE_NAME bash
