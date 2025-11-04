import socket
import threading
import json
import os
import time

DATA_DIR = "/app/data/shared"
DISCOVERY_FILE = os.path.join(DATA_DIR, "discovered_users.json")
CONTACTS_DIR = os.path.join(DATA_DIR, "contacts")

BROADCAST_ADDR = "<broadcast>"  # broadcast to local LAN
PORT = 50000

RUNNING = True
file_lock = threading.Lock()


def _load_json(path):
    if not os.path.exists(path):
        return {}
    try:
        with open(path, "r") as f:
            return json.load(f)
    except json.JSONDecodeError:
        return {}


def _save_json(path, data):
    os.makedirs(os.path.dirname(path), exist_ok=True)
    with file_lock:
        with open(path, "w") as f:
            json.dump(data, f, indent=2)


def _get_user_contacts(username):
    """Return a set of usernames this user has as contacts."""
    path = os.path.join(CONTACTS_DIR, f"{username}.json")
    if not os.path.exists(path):
        return set()
    try:
        with open(path, "r") as f:
            data = json.load(f)
        return set(data.keys())
    except json.JSONDecodeError:
        return set()


def broadcast_presence(username):
    """Send UDP broadcast announcing this user and their contacts."""
    contacts = list(_get_user_contacts(username))
    message = json.dumps({
        "username": username,
        "contacts": contacts,
        "timestamp": time.time()
    })
    sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    sock.setsockopt(socket.SOL_SOCKET, socket.SO_BROADCAST, 1)
    sock.sendto(message.encode(), (BROADCAST_ADDR, PORT))
    sock.close()


def listen_for_users(username):
    """Listen for UDP broadcasts from other users and update discovered_users.json."""
    sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    sock.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)

    # Bind to all interfaces
    try:
        sock.bind(("", PORT))
    except OSError:
        print("[WARN] Could not bind UDP port; another instance might be running.")

    my_contacts = _get_user_contacts(username)

    while RUNNING:
        try:
            data, addr = sock.recvfrom(4096)
            msg = json.loads(data.decode())
            other_user = msg.get("username")
            other_contacts = set(msg.get("contacts", []))
            timestamp = msg.get("timestamp", time.time())

            if not other_user or other_user == username:
                continue

            # Only add if mutual contacts
            if username in other_contacts and other_user in my_contacts:
                discovered = _load_json(DISCOVERY_FILE)
                discovered[other_user] = {
                    "ip": addr[0],
                    "last_seen": timestamp
                }
                _save_json(DISCOVERY_FILE, discovered)
        except Exception:
            continue

    sock.close()


def periodic_broadcast(username):
    """Send presence updates periodically."""
    while RUNNING:
        broadcast_presence(username)
        time.sleep(5)


def start_network(username):
    """Start broadcast listener and broadcaster threads."""
    print(f"[INFO] Starting LAN broadcast network for {username}")
    os.makedirs(DATA_DIR, exist_ok=True)

    listener = threading.Thread(target=listen_for_users, args=(username,), daemon=True)
    broadcaster = threading.Thread(target=periodic_broadcast, args=(username,), daemon=True)

    listener.start()
    broadcaster.start()


def remove_from_discovery(username):
    """Remove a user from discovered_users.json on logout/exit."""
    discovered = _load_json(DISCOVERY_FILE)
    if username in discovered:
        del discovered[username]
        _save_json(DISCOVERY_FILE, discovered)
        print(f"[INFO] {username} removed from discovered users.")