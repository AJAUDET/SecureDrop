import socket
import struct
import threading
import json
import time

MULTICAST_GROUP = "224.1.1.1"
PORT = 50000
TTL = 2  # LAN hop count
RUNNING = True

# --- Config ---
USE_MULTICAST = False  # True for LAN; False for hotspot or direct test
TARGET_IP = "224.1.1.1" if USE_MULTICAST else "255.255.255.255"

# --- Runtime tracker ---
last_self_msg = 0
last_other_msg = 0


def broadcast_presence(username):
    """Continuously broadcast UDP messages announcing this user."""
    sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM, socket.IPPROTO_UDP)

    if USE_MULTICAST:
        sock.setsockopt(socket.IPPROTO_IP, socket.IP_MULTICAST_TTL, struct.pack("b", TTL))
    else:
        sock.setsockopt(socket.SOL_SOCKET, socket.SO_BROADCAST, 1)

    while RUNNING:
        message = json.dumps({
            "username": username,
            "timestamp": time.time()
        })
        sock.sendto(message.encode(), (TARGET_IP, PORT))
        print(f"[BROADCAST] Sent UDP message from {username} to {TARGET_IP}")
        time.sleep(5)

    sock.close()


def listen_for_users(username):
    """Listen for UDP messages and detect if others are visible."""
    global last_self_msg, last_other_msg

    sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM, socket.IPPROTO_UDP)
    sock.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
    sock.bind(("", PORT))

    if USE_MULTICAST:
        mreq = struct.pack("4sl", socket.inet_aton(TARGET_IP), socket.INADDR_ANY)
        sock.setsockopt(socket.IPPROTO_IP, socket.IP_ADD_MEMBERSHIP, mreq)

    print(f"[LISTEN] Listening for UDP on {TARGET_IP}:{PORT}...")
    my_ip = socket.gethostbyname(socket.gethostname())
    seen_others = set()
    start_time = time.time()

    while RUNNING:
        try:
            data, addr = sock.recvfrom(4096)
            msg = json.loads(data.decode())
            other_user = msg.get("username")
            timestamp = msg.get("timestamp", time.time())

            if not other_user:
                continue

            if addr[0] == my_ip or other_user == username:
                # This is our own message (loopback)
                last_self_msg = time.time()
                continue

            last_other_msg = time.time()
            seen_others.add(other_user)
            time_str = time.strftime("%H:%M:%S", time.localtime(timestamp))
            print(f"[RECEIVED] {other_user} @ {addr[0]} | {time_str}")

        except Exception:
            continue

        # Check every 30 seconds for connectivity status
        if time.time() - start_time > 30:
            start_time = time.time()
            if last_other_msg < last_self_msg:
                print("\n[WARN] No other users detected — your UDP messages are only looping back.")
                print("       This likely means your hotspot or network is blocking broadcast/multicast.\n")
                print("       ➤ Try switching to a home Wi-Fi or wired LAN for proper discovery.\n")
            elif seen_others:
                print(f"[INFO] Connected to {len(seen_others)} peers via UDP broadcast.")
            else:
                print("[INFO] Still waiting for discovery packets from other users...")

    sock.close()


def start_network(username):
    """Start both broadcaster and listener threads."""
    print(f"[INFO] Starting UDP network test for {username}")
    listener = threading.Thread(target=listen_for_users, args=(username,), daemon=True)
    broadcaster = threading.Thread(target=broadcast_presence, args=(username,), daemon=True)

    listener.start()
    broadcaster.start()


if __name__ == "__main__":
    user = input("Enter username: ").strip()
    start_network(user)

    try:
        while True:
            time.sleep(1)
    except KeyboardInterrupt:
        print("\n[INFO] Shutting down...")
        RUNNING = False
        time.sleep(1)