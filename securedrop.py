import os
import sys
import socket
import struct
import pwinput
import json
import atexit
import signal
import time
import user_alt as user
import verify_alt as verify
from contactmanage_alt import (
    add_contact,
    list_contacts,
    verify_contact,
    admin_list,
    admin_clear,
    remove_contact
)
from network_alt import start_network, remove_from_discovery, DATA_DIR

from welcome import welcome_msg

PRIVATE_DIR = "/app/data/private"
PASSWD_FILE = os.path.join(DATA_DIR, "passwd.json")

# Map CLI commands to functions
command_map = {
    "add": add_contact,
    "list": list_contacts,
    "verify": verify_contact,
    "remove": remove_contact,
    "admin_list": admin_list,
    "admin_clear": admin_clear,
    "clear": lambda _: os.system("clear"),
    "exit": lambda username: goodbye_msg(username)
}


MULTICAST_GROUP = "224.1.1.1"
PORT = 50000
TEST_TIMEOUT = 5  # seconds

def test_udp_discovery():
    print("\n[INFO] Testing UDP discovery on LAN...")

    # Listener socket
    listener = socket.socket(socket.AF_INET, socket.SOCK_DGRAM, socket.IPPROTO_UDP)
    listener.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
    try:
        listener.bind(("", PORT))
    except OSError:
        print("[WARN] Could not bind UDP port. Another instance might be running.")
        return

    mreq = struct.pack("4sl", socket.inet_aton(MULTICAST_GROUP), socket.INADDR_ANY)
    listener.setsockopt(socket.IPPROTO_IP, socket.IP_ADD_MEMBERSHIP, mreq)
    listener.settimeout(TEST_TIMEOUT)

    # Send a test multicast message
    test_sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM, socket.IPPROTO_UDP)
    test_sock.setsockopt(socket.IPPROTO_IP, socket.IP_MULTICAST_TTL, struct.pack("b", 2))

    test_message = f"SECURE_DROP_UDP_TEST:{username}:{time.time()}"
    test_sock.sendto(test_message.encode(), (MULTICAST_GROUP, PORT))
    test_sock.close()

    print(f"[INFO] Sent test UDP multicast message as '{username}'. Listening for {TEST_TIMEOUT} seconds...")

    start_time = time.time()
    found_other_devices = False

    while time.time() - start_time < TEST_TIMEOUT:
        try:
            data, addr = listener.recvfrom(1024)
            data_decoded = data.decode()

            # Ignore our own test message
            if data_decoded.startswith(f"SECURE_DROP_UDP_TEST:{username}:"):
                continue

            print(f"[SUCCESS] Received UDP message from {addr}: {data_decoded}")
            found_other_devices = True

        except socket.timeout:
            break
        except Exception:
            continue

    listener.close()

    if not found_other_devices:
        print("[WARN] No other devices responded to UDP discovery. Check network/firewall.")
    else:
        print("[INFO] UDP discovery test successful. Other devices detected on LAN.\n")


def goodbye_msg(username):
    print(f"\n[INFO] Logging out {username}...")
    remove_from_discovery(username)
    print("[INFO] You have been removed from discovered users.")
    time.sleep(0.5)
    print("[INFO] Thank you for using Secure Drop! Goodbye!")
    sys.exit(0)


def main(username):
    while True:
        try:
            cmd = input(f"{username}@securedrop.com: ").strip().lower()
            if cmd in command_map:
                command_map[cmd](username)
            elif cmd == "help":
                print("Available commands: add, list, verify, remove, clear, exit")
                if username.lower() == "admin":
                    print("admin_list, admin_clear")
            elif cmd == "":
                continue
            else:
                print("Unknown command. Type 'help' for a list of commands.")
        except KeyboardInterrupt:
            goodbye_msg(username)


def init_passwd_file():
    if os.path.exists(PASSWD_FILE):
        try:
            with open(PASSWD_FILE, "r") as f:
                data = json.load(f)
            if "Users" not in data:
                data = {"Users": {}}
        except json.JSONDecodeError:
            data = {"Users": {}}
    else:
        data = {"Users": {}}
        with open(PASSWD_FILE, "w") as f:
            json.dump(data, f, indent=2)
    return data


def create_user_dirs(username):
    user_dir = os.path.join(DATA_DIR, username)
    for subdir in ["contacts", "public_keys", "private_keys"]:
        os.makedirs(os.path.join(user_dir, subdir), exist_ok=True)


def login_or_register(data):
    action = input("Do you want to (l)ogin or (r)egister? [l/r]: ").strip().lower()
    if action == "r":
        username = input("Enter your Username: ").strip()
        password = pwinput.pwinput(prompt="Enter your Password: ", mask="*")
        email = input(f"Enter your Email for {username}: ").strip()
        while not email:
            print("Email cannot be empty.")
            email = input(f"Enter your Email for {username}: ").strip()

        user.add_user(data_dir=DATA_DIR, auto_user=username, auto_pass=password, email=email)
        verify.verify(username, password, data_dir=DATA_DIR)
        return username, password

    elif action == "l":
        username = input("Enter your Username: ").strip()
        password = pwinput.pwinput(prompt="Enter your Password: ", mask="*")
        verify.verify(username, password, data_dir=DATA_DIR)
        return username, password

    else:
        print("Invalid option. Exiting.")
        sys.exit(1)


if __name__ == "__main__":
    os.makedirs(DATA_DIR, exist_ok=True)
    os.makedirs(PRIVATE_DIR, exist_ok=True)

    # --- Load or initialize password file ---
    data = init_passwd_file()

    # --- Try automated login via environment variables ---
    username = os.environ.get("USER_NAME")
    password_env = os.environ.get("USER_PASSWORD")
    email_env = os.environ.get("USER_EMAIL")

    if username and username in data["Users"]:
        password_env = password_env or pwinput.pwinput(f"Enter password for {username}: ", mask="*")
        verify.verify(username, password_env, data_dir=DATA_DIR)
    else:
        username, password_env = login_or_register(data)

    # --- Setup user environment ---
    create_user_dirs(username)

    # --- Register cleanup handlers ---
    atexit.register(remove_from_discovery, username)
    signal.signal(signal.SIGTERM, lambda *_: goodbye_msg(username))
    signal.signal(signal.SIGINT, lambda *_: goodbye_msg(username))

    # --- Start UDP multicast LAN discovery ---
    print(f"[INFO] Starting network discovery for {username}...")
    start_network(username)  # This now merges discovered_users.json safely
    test_udp_discovery()

    # --- Greet the user ---
    welcome_msg(username)

    # --- Start main CLI loop ---
    main(username)