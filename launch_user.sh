#!/bin/bash
# launch_user.sh — Launch SecureDrop container for a specific user

set -e

# --- CONFIG ---
IMAGE_NAME="securedrop-docker_user_container"
NETWORK_NAME="securedrop_lan"
BASE_DATA_DIR="$(pwd)/data"   # all user data lives here

# --- ARGUMENT CHECK ---
if [ -z "$1" ]; then
  echo "Usage: $0 <username>"
  exit 1
fi

# --- ENSURE IMAGE EXISTS ---
if ! docker image inspect "$IMAGE_NAME" >/dev/null 2>&1; then
  echo "[+] Image '$IMAGE_NAME' not found. Building it now..."
  docker build -t "$IMAGE_NAME" .
fi

USER_NAME="$1"
USER_VOLUME="${BASE_DATA_DIR}/${USER_NAME}"

# --- CREATE USER DATA STRUCTURE ---
echo "[+] Setting up data directories for user: $USER_NAME"
mkdir -p "${USER_VOLUME}/contacts"
mkdir -p "${USER_VOLUME}/public_keys"
mkdir -p "${USER_VOLUME}/private_keys"
mkdir -p "${USER_VOLUME}/messages"

echo "[+] User data directory prepared at ${USER_VOLUME}"

# --- CHECK NETWORK ---
if ! docker network inspect "$NETWORK_NAME" >/dev/null 2>&1; then
  echo "[+] Network '$NETWORK_NAME' not found. Creating..."
  docker network create --driver=macvlan \
    --subnet=192.168.1.0/24 \
    --ip-range=192.168.1.200/29 \
    --gateway=192.168.1.1 \
    -o parent=eth0 \
    "$NETWORK_NAME"
fi

# --- CLEANUP EXISTING CONTAINER ---
echo "[+] Cleaning up old container (if any)..."
docker rm -f "${USER_NAME}_container" >/dev/null 2>&1 || true

# --- LAUNCH CONTAINER ---
echo "[+] Launching SecureDrop container for $USER_NAME..."
docker run -it --rm \
  --name "${USER_NAME}_container" \
  -e USER_NAME="$USER_NAME" \
  -v "${USER_VOLUME}:/app/data" \
  --network "$NETWORK_NAME" \
  "$IMAGE_NAME" \
  bash