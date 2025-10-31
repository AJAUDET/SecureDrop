import os
import json
import time
import socket
import threading

DISCOVERY_FILE = "/app/data/discovered_users.json"
CONTACTS_DIR = "/app/data/contacts"
CHECK_INTERVAL = 5  # seconds
PING_PORT = 50001
file_lock = threading.Lock()


def get_local_ip():
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


def ping_listener():
    sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    sock.bind(("0.0.0.0", PING_PORT))
    while True:
        data, addr = sock.recvfrom(1024)
        if data == b"ping":
            sock.sendto(b"pong", addr)


def ping_user(ip):
    sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    sock.settimeout(1)
    try:
        sock.sendto(b"ping", (ip, PING_PORT))
        data, _ = sock.recvfrom(1024)
        return data == b"pong"
    except Exception:
        return False
    finally:
        sock.close()


def update_discovery(username, local_ip):
    os.makedirs(os.path.dirname(DISCOVERY_FILE), exist_ok=True)
    with file_lock:
        if os.path.exists(DISCOVERY_FILE):
            try:
                with open(DISCOVERY_FILE, "r") as f:
                    data = json.load(f)
            except json.JSONDecodeError:
                data = {}
        else:
            data = {}

        data[username] = {"ip": local_ip, "online": True}

        with open(DISCOVERY_FILE, "w") as f:
            json.dump(data, f, indent=2)


def check_contacts(username):
    while True:
        local_ip = get_local_ip()
        update_discovery(username, local_ip)

        # Load contacts + discovered users
        my_contacts = get_user_contacts(username)
        if not my_contacts:
            time.sleep(CHECK_INTERVAL)
            continue

        with file_lock:
            try:
                with open(DISCOVERY_FILE, "r") as f:
                    discovered = json.load(f)
            except (FileNotFoundError, json.JSONDecodeError):
                discovered = {}

        changed = False

        for contact_username, info in discovered.items():
            if contact_username == username:
                continue

            # Only check mutual contacts
            if not is_mutual_contact(username, contact_username):
                continue

            ip = info.get("ip")
            if not ip:
                continue

            reachable = ping_user(ip)
            if info.get("online") != reachable:
                discovered[contact_username]["online"] = reachable
                changed = True

        if changed:
            with file_lock:
                with open(DISCOVERY_FILE, "w") as f:
                    json.dump(discovered, f, indent=2)

        time.sleep(CHECK_INTERVAL)


def start_network(username):
    local_ip = get_local_ip()
    update_discovery(username, local_ip)
    threading.Thread(target=ping_listener, daemon=True).start()
    threading.Thread(target=check_contacts, args=(username,), daemon=True).start()