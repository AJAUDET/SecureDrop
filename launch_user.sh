#!/bin/bash
set -e

# ======================================
# SecureDrop Docker Launcher (Cross-Platform)
# ======================================
# Usage:
#   ./launch_user.sh --init
#   ./launch_user.sh <username> <password> <email>
# ======================================

USERNAME="$1"
PASSWORD="$2"
EMAIL="$3"
IMAGE_NAME="securedrop-docker_user_container"
NETWORK_NAME="securedrop_bridge"

# ======================================
# Determine platform and set shared_data path
# ======================================
if [[ "$OSTYPE" == "msys" || "$OSTYPE" == "win32" ]]; then
    # Windows Git Bash / Docker Desktop
    SHARED_DATA="$(pwd -W)/shared_data"
else
    # Linux / macOS
    SCRIPT_DIR="$(cd "$(dirname "$0")" && pwd)"
    SHARED_DATA="${SCRIPT_DIR}/shared_data"
fi

# Remove hidden carriage returns if any
SHARED_DATA="${SHARED_DATA//$'\r'/}"

# Create shared data directory
mkdir -p "$SHARED_DATA"
chmod 777 "$SHARED_DATA"
echo "[INFO] Using shared data directory: $SHARED_DATA"

# ======================================
# Detect mode (--init or per-user)
# ======================================
if [ "$1" == "--init" ]; then
    MODE="init"
    echo "[INFO] Launching uninitialized SecureDrop container..."
else
    if [ -z "$USERNAME" ] || [ -z "$PASSWORD" ] || [ -z "$EMAIL" ]; then
        echo "Usage:"
        echo "  $0 <username> <password> <email>"
        echo "  $0 --init"
        exit 1
    fi
fi

# ======================================
# Ensure Docker network exists
# ======================================
if ! docker network ls --format '{{.Name}}' | grep -q "^${NETWORK_NAME}$"; then
    echo "[INFO] Creating network $NETWORK_NAME..."
    docker network create --driver bridge "$NETWORK_NAME"
else
    echo "[INFO] Using existing Docker network: $NETWORK_NAME"
fi

# ======================================
# Launch uninitialized container
# ======================================
if [ "$MODE" == "init" ]; then
    CONTAINER_NAME="securedrop_uninitialized"

    # Remove old instance if exists
    if docker ps -a --format '{{.Names}}' | grep -q "^${CONTAINER_NAME}$"; then
        echo "[INFO] Removing existing uninitialized container..."
        docker rm -f "$CONTAINER_NAME"
    fi

    echo "[INFO] Starting uninitialized container..."
    docker run -it \
        --name "$CONTAINER_NAME" \
        --network "$NETWORK_NAME" \
        -v "${SHARED_DATA}:/app/data/shared" \
        "$IMAGE_NAME" \
        bash -c "echo '[INFO] Booted uninitialized container. Run python3 securedrop.py to create/login a user.'; exec bash"

    echo "[INFO] Uninitialized container session ended."
    docker rm -f "$CONTAINER_NAME" >/dev/null 2>&1 || true
    exit 0
fi

# ======================================
# User container setup
# ======================================
CONTAINER_NAME="${USERNAME}_container"
SCRIPT_DIR="$(cd "$(dirname "$0")" && pwd)"
USER_ROOT="${SCRIPT_DIR}/users/${USERNAME}"
USER_AUTH="${USER_ROOT}/auth"
USER_DATA="${USER_ROOT}/data"

mkdir -p "$USER_AUTH" "$USER_DATA"
chmod -R 700 "$USER_ROOT"

# Remove existing container if it exists
if docker ps -a --format '{{.Names}}' | grep -q "^${CONTAINER_NAME}$"; then
    echo "[INFO] Removing existing container: $CONTAINER_NAME"
    docker rm -f "$CONTAINER_NAME"
fi

echo "[INFO] Launching SecureDrop container for user: $USERNAME"
echo "[DEBUG] Mounting volumes:"
echo "  Auth:   $USER_AUTH -> /app/auth"
echo "  Data:   $USER_DATA -> /app/data/private"
echo "  Shared: $SHARED_DATA -> /app/data/shared"

docker run -it \
    --name "$CONTAINER_NAME" \
    --hostname "${USERNAME}-securedrop" \
    --network "$NETWORK_NAME" \
    --env USER_NAME="$USERNAME" \
    --env USER_PASSWORD="$PASSWORD" \
    --env USER_EMAIL="$EMAIL" \
    -v "${USER_AUTH}:/app/auth" \
    -v "${USER_DATA}:/app/data/private" \
    -v "${SHARED_DATA}:/app/data/shared" \
    "$IMAGE_NAME" \
    bash -c "python3 securedrop.py; cd /app/data/private; exec bash"

# ======================================
# Cleanup after exit
# ======================================
if docker ps -a --format '{{.Names}}' | grep -q "^${CONTAINER_NAME}$"; then
    echo "[INFO] Cleaning up container: $CONTAINER_NAME"
    docker rm -f "$CONTAINER_NAME"
fi

echo "[INFO] SecureDrop session for $USERNAME closed."