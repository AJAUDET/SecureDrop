import verify
import pwinput
import user as user_module
import os
import sys
import threading
import time
from pathlib import Path
import requests
from cryptography.fernet import Fernet
from contactmanage import add_contact, list_contacts, verify_contact, admin_list, admin_clear
from network import start_network
from welcome import welcome_msg

USER_ID = os.getenv("USER_ID")
USER_NAME = os.getenv("USER_NAME")
BACKEND_URL = os.getenv("BACKEND_URL", "http://securedrop-backend:8080")

PRIVATE_KEY_DIR = Path("/app/private_keys")
PUBLIC_KEY_DIR = Path("/app/public_keys")
UPLOADS_DIR = Path("/app/uploads")

command_map = {
    "add": add_contact,
    "list": list_contacts,
    "verify": verify_contact,
    "admin_list": admin_list,
    "admin_clear": admin_clear,
    "clear": lambda _: os.system('clear'),
    "exit": lambda _: sys.exit(0)
}

def backend_post(endpoint: str, data: dict):
    try:
        url = f"{BACKEND_URL}/{endpoint}"
        r = requests.post(url, json=data, timeout=5)
        r.raise_for_status()
        return r.json()
    except Exception as e:
        print(f"[Error] Failed to contact backend: {e}")
        return None

def load_user_keypair():
    priv_path = PRIVATE_KEY_DIR / f"{USER_NAME}_private.key"
    pub_path = PUBLIC_KEY_DIR / f"{USER_NAME}_public.key"

    if not priv_path.exists() or not pub_path.exists():
        print(f"[Error] Missing key files for user {USER_NAME}")
        sys.exit(1)

    with open(priv_path, "rb") as f:
        private_key = f.read()
    with open(pub_path, "rb") as f:
        public_key = f.read()

    return private_key, public_key

def get_cipher(private_key: bytes):
    return Fernet(private_key)

# Encrypt a local file and send to backend
def encrypt_and_send_file(cipher, file_path: Path):
    try:
        with open(file_path, "rb") as f:
            data = f.read()
        encrypted = cipher.encrypt(data)
        payload = {
            "user_id": USER_ID,
            "user_name": USER_NAME,
            "message": encrypted.decode("utf-8")
        }
        backend_post("upload", payload)
        file_path.unlink()  # delete after sending
        print(f"[Info] File {file_path.name} encrypted and sent to backend.")
    except Exception as e:
        print(f"[Error] Failed to encrypt/send {file_path}: {e}")

# Monitor uploads directory
def monitor_uploads(cipher):
    UPLOADS_DIR.mkdir(exist_ok=True, parents=True)
    while True:
        for file in UPLOADS_DIR.glob("*.txt"):
            encrypt_and_send_file(cipher, file)
        time.sleep(5)

def main_cli():
    while True:
        cmd = input(f"{USER_NAME}@securedrop.com: ").strip()
        if cmd in command_map:
            command_map[cmd](USER_NAME)
        elif cmd == "help":
            print("Available commands: add, list, verify, clear, exit")
            if USER_NAME == "admin":
                print("admin_list, admin_clear")
        else:
            print("Unknown command. Type 'help' for a list of commands.")

def main():
    global USER_NAME

    # Use container environment variables if present
    if not USER_NAME:
        login = input("Would you like to register (y/n): ").strip().lower()
        if login == 'y':
            user_module.add_user()
        USER_NAME = input("Enter your Username: ").strip()
        pwd = pwinput.pwinput(prompt="Enter your Password: ", mask='*')
        verify.verify(USER_NAME, pwd)

    # Load keys and initialize cipher
    private_key, public_key = load_user_keypair()
    cipher = get_cipher(private_key)

    # Register user with backend
    backend_post("register", {"user_id": USER_ID, "user_name": USER_NAME})

    # Start background thread to monitor uploads
    threading.Thread(target=monitor_uploads, args=(cipher,), daemon=True).start()

    # Start network and welcome
    start_network(USER_NAME)
    welcome_msg(USER_NAME)

    # Start CLI loop
    main_cli()

if __name__ == "__main__":
    main()
