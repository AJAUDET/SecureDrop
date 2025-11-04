import socket
import struct
import threading
import json
import os
import time

DATA_DIR = "/app/data/shared"
DISCOVERY_FILE = os.path.join(DATA_DIR, "discovered_users.json")

# Multicast configuration
MULTICAST_GROUP = "224.1.1.1"
PORT = 50000
TTL = 2  # hop count, stays within local network

RUNNING = True


def _load_discovered():
    if not os.path.exists(DISCOVERY_FILE):
        return {}
    try:
        with open(DISCOVERY_FILE, "r") as f:
            return json.load(f)
    except json.JSONDecodeError:
        return {}


def _save_discovered(data):
    os.makedirs(DATA_DIR, exist_ok=True)
    with open(DISCOVERY_FILE, "w") as f:
        json.dump(data, f, indent=2)


def broadcast_presence(username):
    """
    Sends multicast beacon announcing this user.
    """
    message = json.dumps({"username": username, "timestamp": time.time()})
    sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM, socket.IPPROTO_UDP)
    sock.setsockopt(socket.IPPROTO_IP, socket.IP_MULTICAST_TTL, struct.pack('b', TTL))
    sock.sendto(message.encode(), (MULTICAST_GROUP, PORT))
    sock.close()


def listen_for_users(username):
    """
    Listens for multicast announcements from other users.
    """
    sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM, socket.IPPROTO_UDP)
    sock.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)

    try:
        sock.bind(("", PORT))
    except OSError:
        print("[WARN] Could not bind UDP port; another instance might be running.")

    mreq = struct.pack("4sl", socket.inet_aton(MULTICAST_GROUP), socket.INADDR_ANY)
    sock.setsockopt(socket.IPPROTO_IP, socket.IP_ADD_MEMBERSHIP, mreq)

    while RUNNING:
        try:
            data, addr = sock.recvfrom(1024)
            msg = json.loads(data.decode())
            user = msg.get("username")
            if user and user != username:
                discovered = _load_discovered()
                discovered[user] = {
                    "ip": addr[0],
                    "last_seen": msg.get("timestamp", time.time())
                }
                _save_discovered(discovered)
        except Exception:
            pass

    sock.close()


def periodic_broadcast(username):
    """
    Periodically send presence updates every few seconds.
    """
    while RUNNING:
        broadcast_presence(username)
        time.sleep(5)


def start_network(username):
    """
    Start the multicast listener and broadcaster threads.
    """
    print(f"[INFO] Starting multicast network for {username} on {MULTICAST_GROUP}:{PORT}")
    os.makedirs(DATA_DIR, exist_ok=True)

    listener = threading.Thread(target=listen_for_users, args=(username,), daemon=True)
    broadcaster = threading.Thread(target=periodic_broadcast, args=(username,), daemon=True)

    listener.start()
    broadcaster.start()


def remove_from_discovery(username):
    """
    Remove a user from the discovered list on logout/exit.
    """
    discovered = _load_discovered()
    if username in discovered:
        del discovered[username]
        _save_discovered(discovered)
        print(f"[INFO] {username} removed from discovered users.")