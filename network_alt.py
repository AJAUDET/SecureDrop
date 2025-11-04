import os
import json
import time
import socket
import threading

DISCOVERY_FILE = "/app/data/shared/discovered_users.json"
CONTACTS_DIR = "/app/data/shared/contacts"
BROADCAST_PORT = 50001
CHECK_INTERVAL = 5  # seconds
EXPIRATION_TIME = CHECK_INTERVAL * 2  # mark offline if not seen within this window
file_lock = threading.Lock()


def get_local_ip():
    """Get the local network IP of this host."""
    s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    try:
        s.connect(("8.8.8.8", 80))
        ip = s.getsockname()[0]
    except Exception:
        ip = "127.0.0.1"
    finally:
        s.close()
    return ip


def get_user_contacts(username):
    contacts_file = os.path.join(CONTACTS_DIR, f"{username}.json")
    if not os.path.exists(contacts_file):
        return {}
    try:
        with open(contacts_file, "r") as f:
            return json.load(f)
    except json.JSONDecodeError:
        return {}


def is_mutual_contact(user_a, user_b):
    contacts_a = get_user_contacts(user_a)
    contacts_b = get_user_contacts(user_b)
    return user_b in contacts_a and user_a in contacts_b


def broadcast_presence(username):
    """Continuously broadcast this user's presence to the local network."""
    sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    sock.setsockopt(socket.SOL_SOCKET, socket.SO_BROADCAST, 1)

    local_ip = get_local_ip()

    while True:
        message = json.dumps({
            "username": username,
            "ip": local_ip,
            "status": "online",
            "timestamp": time.time()
        }).encode("utf-8")

        try:
            sock.sendto(message, ("<broadcast>", BROADCAST_PORT))
        except Exception as e:
            print(f"[WARN] Broadcast failed: {e}")

        time.sleep(CHECK_INTERVAL)


def listen_for_broadcasts(username):
    """Listen for broadcast messages from other users."""
    sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    sock.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
    sock.bind(("", BROADCAST_PORT))

    print(f"[INFO] Listening for UDP broadcasts on port {BROADCAST_PORT}...")

    while True:
        try:
            data, addr = sock.recvfrom(1024)
            message = json.loads(data.decode("utf-8"))
            sender = message.get("username")
            sender_ip = message.get("ip")
            timestamp = message.get("timestamp", time.time())

            if sender == username:
                continue  # Ignore our own broadcast

            if not is_mutual_contact(username, sender):
                continue  # Only accept mutual contacts

            with file_lock:
                if os.path.exists(DISCOVERY_FILE):
                    try:
                        with open(DISCOVERY_FILE, "r") as f:
                            discovered = json.load(f)
                        # Handle old or malformed files
                        if not isinstance(discovered, dict):
                            discovered = {}
                    except json.JSONDecodeError:
                        discovered = {}
                else:
                    discovered = {}

                discovered[sender] = {
                    "ip": sender_ip,
                    "online": True,
                    "last_seen": timestamp
                }

                with open(DISCOVERY_FILE, "w") as f:
                    json.dump(discovered, f, indent=2)

        except Exception as e:
            print(f"[WARN] Broadcast listener error: {e}")


def cleanup_discovery(username):
    """Mark users offline if not seen recently."""
    while True:
        now = time.time()
        changed = False

        with file_lock:
            if not os.path.exists(DISCOVERY_FILE):
                time.sleep(CHECK_INTERVAL)
                continue

            try:
                with open(DISCOVERY_FILE, "r") as f:
                    data = json.load(f)
            except json.JSONDecodeError:
                data = {}

            for user, info in list(data.items()):
                if user == username:
                    continue

                last_seen = info.get("last_seen", 0)
                online = info.get("online", False)
                if now - last_seen > EXPIRATION_TIME:
                    if online:  # was previously online
                        data[user]["online"] = False
                        changed = True

            if changed:
                with open(DISCOVERY_FILE, "w") as f:
                    json.dump(data, f, indent=2)

        time.sleep(CHECK_INTERVAL)


def remove_from_discovery(username):
    with file_lock:
        if not os.path.exists(DISCOVERY_FILE):
            return
        try:
            with open(DISCOVERY_FILE, "r") as f:
                data = json.load(f)
        except json.JSONDecodeError:
            data = {}

        if username in data:
            del data[username]
            with open(DISCOVERY_FILE, "w") as f:
                json.dump(data, f, indent=2)
            print(f"[INFO] {username} removed from discovered users.")


def start_network(username):
    """Start the UDP broadcast discovery network."""
    os.makedirs(os.path.dirname(DISCOVERY_FILE), exist_ok=True)
    local_ip = get_local_ip()
    print(f"[INFO] Starting broadcast network as {username} ({local_ip})")

    # Threads: one to broadcast, one to listen, one to cleanup
    threading.Thread(target=broadcast_presence, args=(username,), daemon=True).start()
    threading.Thread(target=listen_for_broadcasts, args=(username,), daemon=True).start()
    threading.Thread(target=cleanup_discovery, args=(username,), daemon=True).start()