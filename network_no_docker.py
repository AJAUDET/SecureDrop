import socket
import struct
import threading
import json
import time

# --------------------------
# Configuration
# --------------------------
MULTICAST_GROUP = "224.1.1.1"
PORT = 50000
TTL = 2  # LAN hop count
RUNNING = True

USE_MULTICAST = False  # True for LAN; False for hotspot / direct test
TARGET_IP = MULTICAST_GROUP if USE_MULTICAST else "255.255.255.255"

# --------------------------
# Runtime trackers
# --------------------------
last_self_msg = 0
last_other_msg = 0


# --------------------------
# Broadcast function
# --------------------------
def broadcast_presence(username):
    """Continuously broadcast UDP presence messages."""
    sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM, socket.IPPROTO_UDP)
    
    if USE_MULTICAST:
        sock.setsockopt(socket.IPPROTO_IP, socket.IP_MULTICAST_TTL, struct.pack("b", TTL))
    else:
        sock.setsockopt(socket.SOL_SOCKET, socket.SO_BROADCAST, 1)

    print(f"[INFO] Broadcasting UDP presence as '{username}' to {TARGET_IP}:{PORT}")

    while RUNNING:
        try:
            message = json.dumps({
                "username": username,
                "timestamp": time.time()
            })
            sock.sendto(message.encode(), (TARGET_IP, PORT))
            print(f"[BROADCAST] Sent UDP message from {username}")
            time.sleep(5)
        except Exception as e:
            print(f"[ERROR] Broadcast failed: {e}")
            time.sleep(5)

    sock.close()


# --------------------------
# Listener function
# --------------------------
def listen_for_users(username):
    """Listen for UDP messages and track other users."""
    global last_self_msg, last_other_msg

    sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM, socket.IPPROTO_UDP)
    sock.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
    sock.bind(("", PORT))

    if USE_MULTICAST:
        mreq = struct.pack("4sl", socket.inet_aton(TARGET_IP), socket.INADDR_ANY)
        sock.setsockopt(socket.IPPROTO_IP, socket.IP_ADD_MEMBERSHIP, mreq)

    my_ip = socket.gethostbyname(socket.gethostname())
    seen_others = set()
    start_time = time.time()

    print(f"[LISTEN] Listening for UDP on {TARGET_IP}:{PORT}...")

    while RUNNING:
        try:
            data, addr = sock.recvfrom(4096)
            msg = json.loads(data.decode())
            other_user = msg.get("username")
            timestamp = msg.get("timestamp", time.time())

            if not other_user:
                continue

            # Ignore own messages
            if addr[0] == my_ip or other_user == username:
                last_self_msg = time.time()
                continue

            last_other_msg = time.time()
            seen_others.add(other_user)
            time_str = time.strftime("%H:%M:%S", time.localtime(timestamp))
            print(f"[RECEIVED] {other_user} @ {addr[0]} | {time_str}")

        except Exception:
            continue

        # Periodically report status
        if time.time() - start_time > 30:
            start_time = time.time()
            if last_other_msg < last_self_msg:
                print("\n[WARN] No other users detected — messages are only looping back.")
            elif seen_others:
                print(f"[INFO] Connected to {len(seen_others)} peers via UDP broadcast.")
            else:
                print("[INFO] Waiting for discovery packets from other users...")

    sock.close()


# --------------------------
# Network starter
# --------------------------
def start_network(username):
    """Start broadcasting and listening in background threads."""
    broadcaster_thread = threading.Thread(target=broadcast_presence, args=(username,), daemon=True)
    listener_thread = threading.Thread(target=listen_for_users, args=(username,), daemon=True)

    broadcaster_thread.start()
    listener_thread.start()

    return broadcaster_thread, listener_thread  # threads returned in case you want to join or monitor


# --------------------------
# Main
# --------------------------
if __name__ == "__main__":
    user = input("Enter username: ").strip()
    start_network(user)

    print("[INFO] UDP network running in background. Press Ctrl+C to exit.")

    try:
        while True:
            time.sleep(1)  # main thread free for other tasks or CLI
    except KeyboardInterrupt:
        print("\n[INFO] Shutting down UDP network...")
        RUNNING = False
        time.sleep(1)