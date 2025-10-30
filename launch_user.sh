#!/bin/bash
# launch_user.sh — Fully automated SecureDrop container launch

set -e

# --- CONFIG ---
IMAGE_NAME="securedrop-docker_user_container"
NETWORK_NAME="securedrop_lan"
TEMPLATE_DIR="$(pwd)/templates"   # optional templates

# --- ARGUMENT CHECK ---
if [ -z "$1" ]; then
  echo "Usage: $0 <username> [password]"
  exit 1
fi

USER_NAME="$1"
USER_PASSWORD="${2:-}"  # optional auto-password
USER_VOLUME="${USER_NAME}_data"

# --- ENSURE DOCKER IMAGE EXISTS ---
if ! docker image inspect "$IMAGE_NAME" >/dev/null 2>&1; then
  echo "[+] Docker image '$IMAGE_NAME' not found. Building..."
  docker build -t "$IMAGE_NAME" .
fi

# --- ENSURE NETWORK EXISTS ---
if ! docker network inspect "$NETWORK_NAME" >/dev/null 2>&1; then
  echo "[+] Creating macvlan network '$NETWORK_NAME'..."
  docker network create --driver=macvlan \
    --subnet=192.168.1.0/24 \
    --ip-range=192.168.1.200/29 \
    --gateway=192.168.1.1 \
    -o parent=eth0 \
    "$NETWORK_NAME"
fi

# --- CREATE USER VOLUME ---
if ! docker volume inspect "$USER_VOLUME" >/dev/null 2>&1; then
  echo "[+] Creating Docker volume for user: $USER_NAME"
  docker volume create "$USER_VOLUME"
  
  # populate first-run template directories inside the volume
  docker run --rm -v "${USER_VOLUME}:/app/data" "$IMAGE_NAME" bash -c "
    mkdir -p /app/data/contacts /app/data/public_keys /app/data/private_keys /app/data/messages
    if [ -d /app/templates ]; then
      cp -r /app/templates/* /app/data/ 2>/dev/null || true
    fi
  "
fi

# --- CLEANUP OLD CONTAINER ---
if docker ps -a --format '{{.Names}}' | grep -q "^${USER_NAME}_container$"; then
  echo "[+] Removing old container..."
  docker rm -f "${USER_NAME}_container" >/dev/null 2>&1 || true
fi

# --- LAUNCH CONTAINER ---
echo "[+] Launching container for user: $USER_NAME"
docker run -it --rm \
  --name "${USER_NAME}_container" \
  -e USER_NAME="$USER_NAME" \
  -e USER_PASSWORD="$USER_PASSWORD" \
  -v "${USER_VOLUME}:/app/data" \
  --network "$NETWORK_NAME" \
  "$IMAGE_NAME" \
  python3 securedrop.py