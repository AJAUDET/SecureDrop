import os
import sys
import socket
import struct
import pwinput
import json
import atexit
import signal
import time
import threading

import user_no_docker as user
import verify_no_docker as verify
from contactmanage import (
    add_contact,
    list_contacts,
    verify_contact,
    admin_list,
    admin_clear
)
from network import start_network
from welcome import welcome_msg

DATA_DIR = "/tmp/securedrop_test/shared"
PRIVATE_DIR = "/tmp/securedrop_test/private"
PASSWD_FILE = os.path.join(DATA_DIR, "passwd.json")

# ----------------------------
# CLI command mapping
# ----------------------------
def goodbye_msg(username):
    print(f"\n[INFO] Logging out {username}...")
    print("[INFO] You have been removed from discovered users.")
    time.sleep(0.5)
    print("[INFO] Thank you for using Secure Drop! Goodbye!")
    sys.exit(0)


command_map = {
    "add": add_contact,
    "list": list_contacts,
    "verify": verify_contact,
    "admin_list": admin_list,
    "admin_clear": admin_clear,
    "clear": lambda _: os.system("clear"),
    "exit": lambda username: goodbye_msg(username)
}

# ----------------------------
# CLI loop
# ----------------------------
def main_cli(username):
    while True:
        try:
            cmd = input(f"{username}@securedrop.com: ").strip().lower()
            if cmd in command_map:
                command_map[cmd](username)
            elif cmd == "help":
                print("Available commands: add, list, verify, clear, exit")
                if username.lower() == "admin":
                    print("admin_list, admin_clear")
            elif cmd == "":
                continue
            else:
                print("Unknown command. Type 'help' for a list of commands.")
        except KeyboardInterrupt:
            goodbye_msg(username)

# ----------------------------
# Initialize password file
# ----------------------------
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

# ----------------------------
# Create per-user directories
# ----------------------------
def create_user_dirs(username):
    user_dir = os.path.join(DATA_DIR, username)
    for subdir in ["contacts", "public_keys", "private_keys"]:
        os.makedirs(os.path.join(user_dir, subdir), exist_ok=True)

# ----------------------------
# Login or register
# ----------------------------
def login_or_register(data):
    action = input("Do you want to (l)ogin or (r)egister? [l/r]: ").strip().lower()
    if action == "r":
        username = input("Enter your Username: ").strip()
        password_value = pwinput.pwinput(prompt="Enter your Password: ", mask="*")
        email = input(f"Enter your Email for {username}: ").strip()
        while not email:
            print("Email cannot be empty.")
            email = input(f"Enter your Email for {username}: ").strip()

        user.add_user(data_dir=DATA_DIR, auto_user=username, auto_pass=password_value, email=email)
        verify.verify(username, password_value, data_dir=DATA_DIR)
        return username, password_value

    elif action == "l":
        username = input("Enter your Username: ").strip()
        password_value = pwinput.pwinput(prompt="Enter your Password: ", mask="*")
        verify.verify(username, password_value, data_dir=DATA_DIR)
        return username, password_value

    else:
        print("Invalid option. Exiting.")
        sys.exit(1)

# ----------------------------
# Main execution
# ----------------------------
if __name__ == "__main__":
    os.makedirs(DATA_DIR, exist_ok=True)
    os.makedirs(PRIVATE_DIR, exist_ok=True)

    data = init_passwd_file()
    username, password_env = login_or_register(data)
    create_user_dirs(username)

    # Cleanup handlers
    signal.signal(signal.SIGTERM, lambda *_: goodbye_msg(username))
    signal.signal(signal.SIGINT, lambda *_: goodbye_msg(username))

    # Start LAN discovery network (broadcast & listen in background)
    print(f"[INFO] Starting network discovery for {username}...")
    start_network(username)  # threads run in background

    # Greet the user
    welcome_msg(username)

    # Start CLI loop
    main_cli(username)