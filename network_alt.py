import socket
import struct
import threading
import json
import os
import time

DATA_DIR = "/app/data/shared"
DISCOVERY_FILE = os.path.join(DATA_DIR, "discovered_users.json")
CONTACTS_DIR = os.path.join(DATA_DIR, "contacts")

# Multicast configuration
MULTICAST_GROUP = "224.1.1.1"
PORT = 50000
TTL = 2  # local network hop count

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
    """Send multicast beacon announcing this user."""
    message = json.dumps({"username": username, "timestamp": time.time()})
    sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM, socket.IPPROTO_UDP)
    sock.setsockopt(socket.IPPROTO_IP, socket.IP_MULTICAST_TTL, struct.pack("b", TTL))
    sock.sendto(message.encode(), (MULTICAST_GROUP, PORT))
    sock.close()


def listen_for_users(username):
    """Listen for multicast announcements from other users."""
    sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM, socket.IPPROTO_UDP)
    sock.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
    try:
        sock.bind(("", PORT))
    except OSError:
        print("[WARN] Could not bind UDP port; another instance might be running.")

    mreq = struct.pack("4sl", socket.inet_aton(MULTICAST_GROUP), socket.INADDR_ANY)
    sock.setsockopt(socket.IPPROTO_IP, socket.IP_ADD_MEMBERSHIP, mreq)

    my_contacts = _get_user_contacts(username)

    while RUNNING:
        try:
            data, addr = sock.recvfrom(1024)
            msg = json.loads(data.decode())
            other_user = msg.get("username")
            timestamp = msg.get("timestamp", time.time())

            if not other_user or other_user == username:
                continue

            # Load the other user's contacts
            other_contacts_file = os.path.join(CONTACTS_DIR, f"{other_user}.json")
            if not os.path.exists(other_contacts_file):
                continue
            with open(other_contacts_file, "r") as f:
                other_contacts = json.load(f)

            # Only add if mutual
            if username in other_contacts and other_user in my_contacts:
                discovered = _load_json(DISCOVERY_FILE)
                discovered[other_user] = {
                    "ip": addr[0],
                    "last_seen": timestamp
                }
                _save_json(DISCOVERY_FILE, discovered)
        except Exception:
            pass

    sock.close()


def periodic_broadcast(username):
    """Send presence updates periodically."""
    while RUNNING:
        broadcast_presence(username)
        time.sleep(5)


def start_network(username):
    """Start the multicast listener and broadcaster threads."""
    print(f"[INFO] Starting multicast network for {username} on {MULTICAST_GROUP}:{PORT}")
    os.makedirs(DATA_DIR, exist_ok=True)

    listener = threading.Thread(target=listen_for_users, args=(username,), daemon=True)
    broadcaster = threading.Thread(target=periodic_broadcast, args=(username,), daemon=True)

    listener.start()
    broadcaster.start()


def remove_from_discovery(username):
    """Remove a user from the discovered list on logout/exit."""
    discovered = _load_json(DISCOVERY_FILE)
    if username in discovered:
        del discovered[username]
        _save_json(DISCOVERY_FILE, discovered)
        print(f"[INFO] {username} removed from discovered users.")