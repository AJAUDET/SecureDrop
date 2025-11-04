import socket
import struct
import threading
import json
import os
import time

DATA_DIR = "/app/data/shared"
DISCOVERY_FILE = os.path.join(DATA_DIR, "discovered_users.json")
CONTACTS_DIR = os.path.join(DATA_DIR, "contacts")
SYNC_INTERVAL = 5  # seconds

MULTICAST_GROUP = "224.1.1.1"
PORT = 50000
TTL = 2

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
    path = os.path.join(CONTACTS_DIR, f"{username}.json")
    if not os.path.exists(path):
        return set()
    try:
        with open(path, "r") as f:
            return set(json.load(f).keys())
    except json.JSONDecodeError:
        return set()

def broadcast_presence(username):
    contacts = list(_get_user_contacts(username))
    message = json.dumps({
        "username": username,
        "contacts": contacts,
        "timestamp": time.time()
    })
    sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM, socket.IPPROTO_UDP)
    sock.setsockopt(socket.IPPROTO_IP, socket.IP_MULTICAST_TTL, struct.pack("b", TTL))
    try:
        sock.sendto(message.encode(), (MULTICAST_GROUP, PORT))
    finally:
        sock.close()

def listen_for_users(username):
    """Listen for multicast on Linux only."""
    if os.name != "posix":
        # Non-Linux: skip UDP listening
        return

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
            data, addr = sock.recvfrom(4096)
            msg = json.loads(data.decode())
            other_user = msg.get("username")
            other_contacts = set(msg.get("contacts", []))
            timestamp = msg.get("timestamp", time.time())

            if not other_user or other_user == username:
                continue

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

def sync_discovery_file(username):
    """Periodically merge discovered_users.json from shared folder."""
    while RUNNING:
        discovered = _load_json(DISCOVERY_FILE)
        for fname in os.listdir(DATA_DIR):
            if fname.endswith(".json") and fname != "discovered_users.json":
                other_file = os.path.join(DATA_DIR, fname)
                try:
                    other_data = _load_json(other_file)
                    discovered.update(other_data)
                except Exception:
                    continue
        _save_json(DISCOVERY_FILE, discovered)
        time.sleep(SYNC_INTERVAL)

def periodic_broadcast(username):
    while RUNNING:
        broadcast_presence(username)
        time.sleep(5)

def start_network(username):
    os.makedirs(DATA_DIR, exist_ok=True)
    print(f"[INFO] Starting LAN network for {username} ({'Linux host network' if os.name == 'posix' else 'shared folder sync'})")

    threads = []
    if os.name == "posix":
        t_listen = threading.Thread(target=listen_for_users, args=(username,), daemon=True)
        threads.append(t_listen)
        t_listen.start()

    t_broadcast = threading.Thread(target=periodic_broadcast, args=(username,), daemon=True)
    t_sync = threading.Thread(target=sync_discovery_file, args=(username,), daemon=True)

    threads.extend([t_broadcast, t_sync])
    t_broadcast.start()
    t_sync.start()

def remove_from_discovery(username):
    discovered = _load_json(DISCOVERY_FILE)
    if username in discovered:
        del discovered[username]
        _save_json(DISCOVERY_FILE, discovered)
        print(f"[INFO] {username} removed from discovered users.")