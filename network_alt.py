import socket
import threading
import json
import os
import time
import sys
from contactmanage_alt import get_user_contacts

DATA_DIR = "/app/data/shared"
DISCOVERY_FILE = os.path.join(DATA_DIR, "discovered_users.json")
PORT = 50000
BROADCAST_INTERVAL = 5  # seconds
RUNNING = True
USE_FILE_FALLBACK = False  # auto-enable if broadcast fails


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


def get_host_ip_and_broadcast():
    """Return host LAN IP and /24 broadcast address."""
    s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    try:
        s.connect(("8.8.8.8", 80))
        local_ip = s.getsockname()[0]
    finally:
        s.close()

    ip_parts = local_ip.split(".")
    ip_parts[-1] = "255"
    broadcast_ip = ".".join(ip_parts)
    return local_ip, broadcast_ip


def broadcast_presence(username, broadcast_ip=None):
    """
    Send presence announcement over LAN. Fallback to shared JSON if broadcast fails.
    """
    global USE_FILE_FALLBACK
    message = json.dumps({"username": username, "timestamp": time.time()})

    if USE_FILE_FALLBACK or broadcast_ip is None:
        # Fallback: write to shared JSON
        discovered = _load_discovered()
        discovered[username] = {"ip": "local", "last_seen": time.time()}
        _save_discovered(discovered)
        return

    try:
        sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        sock.setsockopt(socket.SOL_SOCKET, socket.SO_BROADCAST, 1)
        sock.sendto(message.encode(), (broadcast_ip, PORT))
        sock.close()
    except Exception as e:
        print(f"[WARN] Broadcast failed, using file fallback: {e}")
        USE_FILE_FALLBACK = True


def listen_for_users(username):
    """
    Listen for LAN broadcasts and update discovered_users.json only for mutual contacts.
    """
    global USE_FILE_FALLBACK
    try:
        sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        sock.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        sock.bind(("", PORT))
    except Exception as e:
        print(f"[WARN] Cannot bind UDP port {PORT}, using file fallback: {e}")
        USE_FILE_FALLBACK = True

    while RUNNING:
        if USE_FILE_FALLBACK:
            # Periodically reload shared JSON to detect users
            time.sleep(BROADCAST_INTERVAL)
            continue

        try:
            data, addr = sock.recvfrom(1024)
            msg = json.loads(data.decode())
            remote_user = msg.get("username")
            if not remote_user or remote_user == username:
                continue

            # --- Mutual contact check ---
            local_contacts = get_user_contacts(username)
            remote_contacts = get_user_contacts(remote_user)

            if remote_user in local_contacts and username in remote_contacts:
                discovered = _load_discovered()
                discovered[remote_user] = {
                    "ip": addr[0],
                    "last_seen": msg.get("timestamp", time.time())
                }
                _save_discovered(discovered)

        except Exception:
            pass

    if not USE_FILE_FALLBACK:
        sock.close()


def periodic_broadcast(username, broadcast_ip):
    while RUNNING:
        broadcast_presence(username, broadcast_ip)
        time.sleep(BROADCAST_INTERVAL)


def start_network(username):
    """
    Start listener and broadcaster threads for LAN presence discovery.
    """
    global USE_FILE_FALLBACK
    os.makedirs(DATA_DIR, exist_ok=True)

    # Detect LAN IP and broadcast
    try:
        local_ip, broadcast_ip = get_host_ip_and_broadcast()
        print(f"[INFO] Local IP: {local_ip}, Broadcast IP: {broadcast_ip}")
    except Exception as e:
        print(f"[WARN] Cannot detect LAN IP, using file fallback: {e}")
        USE_FILE_FALLBACK = True
        broadcast_ip = None

    print(f"[INFO] Starting network discovery for {username}...")
    listener = threading.Thread(target=listen_for_users, args=(username,), daemon=True)
    broadcaster = threading.Thread(target=periodic_broadcast, args=(username, broadcast_ip), daemon=True)
    listener.start()
    broadcaster.start()


def remove_from_discovery(username):
    """
    Remove user from discovered_users.json on logout/exit.
    """
    discovered = _load_discovered()
    if username in discovered:
        del discovered[username]
        _save_discovered(discovered)
        print(f"[INFO] {username} removed from discovered users.")