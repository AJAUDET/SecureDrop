import socket
import struct
import threading
import json
import time

MULTICAST_GROUP = "224.1.1.1"
PORT = 50000
TTL = 2  # LAN hop count
RUNNING = True


def broadcast_presence(username):
    """Continuously broadcast UDP messages announcing this user."""
    sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM, socket.IPPROTO_UDP)
    sock.setsockopt(socket.IPPROTO_IP, socket.IP_MULTICAST_TTL, struct.pack("b", TTL))

    while RUNNING:
        message = json.dumps({
            "username": username,
            "timestamp": time.time()
        })
        sock.sendto(message.encode(), (MULTICAST_GROUP, PORT))
        print(f"[BROADCAST] Sent UDP message from {username}")
        time.sleep(5)

    sock.close()


def listen_for_users(username):
    """Listen for UDP multicast messages from other users and print them."""
    sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM, socket.IPPROTO_UDP)
    sock.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
    sock.bind(("", PORT))

    mreq = struct.pack("4sl", socket.inet_aton(MULTICAST_GROUP), socket.INADDR_ANY)
    sock.setsockopt(socket.IPPROTO_IP, socket.IP_ADD_MEMBERSHIP, mreq)

    my_ip = socket.gethostbyname(socket.gethostname())

    print(f"[LISTEN] Listening for UDP broadcasts on {MULTICAST_GROUP}:{PORT}...")

    while RUNNING:
        try:
            data, addr = sock.recvfrom(4096)
            msg = json.loads(data.decode())
            other_user = msg.get("username")
            timestamp = msg.get("timestamp")

            # Ignore own messages
            if not other_user or other_user == username or addr[0] == my_ip:
                continue

            time_str = time.strftime("%H:%M:%S", time.localtime(timestamp))
            print(f"[RECEIVED] {other_user} @ {addr[0]} | {time_str}")
        except Exception:
            continue

    sock.close()


def start_network(username):
    """Start both broadcaster and listener threads."""
    print(f"[INFO] Starting UDP multicast network for {username}")
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