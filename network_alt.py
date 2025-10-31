import socket
import threading
import time
import json
import os

DISCOVERY_FILE = "/app/data/discovered_users.json"
NETWORK_PORT = 50000
LISTEN_INTERVAL = 1
ANNOUNCE_INTERVAL = 5

file_lock = threading.Lock()

def get_bridge_ip():
    s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    try:
        s.connect(("8.8.8.8", 80))
        ip = s.getsockname()[0]
    except Exception:
        ip = "127.0.0.1"
    finally:
        s.close()
    return ip

def listen_for_users():
    sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    sock.bind(("0.0.0.0", NETWORK_PORT))
    sock.settimeout(LISTEN_INTERVAL)

    discovered = {}

    while True:
        try:
            data, addr = sock.recvfrom(1024)
            try:
                msg = json.loads(data.decode("utf-8"))
                username = msg.get("username")
                ip = msg.get("ip")
                if username and ip:
                    discovered[username] = ip
                    with file_lock:
                        os.makedirs(os.path.dirname(DISCOVERY_FILE), exist_ok=True)
                        with open(DISCOVERY_FILE, "w") as f:
                            json.dump(discovered, f, indent=2)
            except json.JSONDecodeError:
                continue
        except socket.timeout:
            continue
        except Exception as e:
            print(f"[WARN] Listener error: {e}")

def announce_presence(username):
    sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    local_ip = get_bridge_ip()

    while True:
        # Read discovered users
        targets = {}
        if os.path.exists(DISCOVERY_FILE):
            with file_lock:
                with open(DISCOVERY_FILE, "r") as f:
                    try:
                        targets = json.load(f)
                    except json.JSONDecodeError:
                        targets = {}

        message = json.dumps({"username": username, "ip": local_ip}).encode("utf-8")

        for user, ip in targets.items():
            if user != username:
                try:
                    sock.sendto(message, (ip, NETWORK_PORT))
                except Exception as e:
                    print(f"[WARN] Failed to announce to {user} ({ip}): {e}")

        time.sleep(ANNOUNCE_INTERVAL)

def start_network(username):
    threading.Thread(target=listen_for_users, daemon=True).start()
    threading.Thread(target=announce_presence, args=(username,), daemon=True).start()
