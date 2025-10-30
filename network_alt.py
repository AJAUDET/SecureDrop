import socket
import threading
import time
import json
import os

# Shared data directory for discovered users
DISCOVERY_FILE = "/app/data/discovered_users.json"
BROADCAST_PORT = 50000
BROADCAST_INTERVAL = 5  # seconds
LISTEN_INTERVAL = 1     # seconds

def get_local_ip():
    """
    Get the container's IP address on the Docker bridge network.
    """
    s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    try:
        # connect to a public IP (won't send data)
        s.connect(("8.8.8.8", 80))
        ip = s.getsockname()[0]
    except Exception:
        ip = "127.0.0.1"
    finally:
        s.close()
    return ip

def broadcast_presence(username):
    """
    Continuously broadcast this user's presence via UDP.
    """
    sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    sock.setsockopt(socket.SOL_SOCKET, socket.SO_BROADCAST, 1)
    broadcast_ip = "<broadcast>"  # Docker bridge supports <broadcast>

    local_ip = get_local_ip()
    message = json.dumps({"username": username, "ip": local_ip}).encode("utf-8")

    while True:
        try:
            sock.sendto(message, (broadcast_ip, BROADCAST_PORT))
        except Exception as e:
            print(f"[WARN] Broadcast failed: {e}")
        time.sleep(BROADCAST_INTERVAL)

def listen_for_users():
    """
    Listen for broadcast messages from other users.
    """
    sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    sock.bind(("", BROADCAST_PORT))
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
                    # persist to shared file
                    os.makedirs(os.path.dirname(DISCOVERY_FILE), exist_ok=True)
                    with open(DISCOVERY_FILE, "w") as f:
                        json.dump(discovered, f, indent=2)
            except json.JSONDecodeError:
                continue
        except socket.timeout:
            continue
        except Exception as e:
            print(f"[WARN] Listener error: {e}")

def start_network(username):
    """
    Start broadcasting and listening threads.
    """
    threading.Thread(target=broadcast_presence, args=(username,), daemon=True).start()
    threading.Thread(target=listen_for_users, daemon=True).start()
