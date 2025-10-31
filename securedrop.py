import os
import sys
import pwinput
import user_alt as user
import verify_alt as verify
from contactmanage_alt import add_contact, list_contacts, verify_contact, admin_list, admin_clear
from network_alt import start_network
from welcome import welcome_msg
import json

DATA_ROOT = "/app/data/shared"
PASSWD_FILE = os.path.join(DATA_ROOT, "passwd.json")

command_map = {
    "add": add_contact,
    "list": list_contacts,
    "verify": verify_contact,
    "admin_list": admin_list,
    "admin_clear": admin_clear,
    "clear": lambda _: os.system("clear"),
    "exit": lambda _: sys.exit(0)
}

def main(username):
    while True:
        cmd = input(f"{username}@securedrop.com: ").strip()
        if cmd in command_map:
            command_map[cmd](username)
        elif cmd == "help":
            print("Available commands: add, list, verify, clear, exit")
            if username.lower() == "admin":
                print("admin_list, admin_clear")
        else:
            print("Unknown command. Type 'help' for a list of commands.")

if __name__ == "__main__":
    os.makedirs(DATA_ROOT, exist_ok=True)

    # Load existing users
    if os.path.exists(PASSWD_FILE):
        try:
            with open(PASSWD_FILE, "r") as f:
                data = json.load(f)
        except json.JSONDecodeError:
            data = {"Users": {}}
    else:
        data = {"Users": {}}
        with open(PASSWD_FILE, "w") as f:
            json.dump(data, f, indent=2)

    # Get environment variables for automated login
    username = os.environ.get("USER_NAME")
    password_env = os.environ.get("USER_PASSWORD")
    email_env = os.environ.get("USER_EMAIL")

    # --- Automated login if username exists ---
    if username and username in data["Users"]:
        password_env = password_env or pwinput.pwinput(f"Enter password for {username}: ", mask="*")
        verify.verify(username, password_env, data_dir=DATA_ROOT)

    # --- Automated user creation if username does not exist ---
    elif username and username not in data["Users"]:
        password_env = password_env or pwinput.pwinput(f"Create password for {username}: ", mask="*")
        if not email_env:
            email_env = input(f"Enter email for {username}: ").strip()
            while not email_env:
                print("Email cannot be empty.")
                email_env = input(f"Enter email for {username}: ").strip()
        user.add_user(data_dir=DATA_ROOT, auto_user=username, auto_pass=password_env, email=email_env)

    # --- Interactive login/register ---
    else:
        action = input("Do you want to (l)ogin or (r)egister? [l/r]: ").strip().lower()
        if action == "r":
            username = input("Enter your Username: ").strip()
            password_env = pwinput.pwinput(prompt="Enter your Password: ", mask="*")
            email_env = input(f"Enter your Email for {username}: ").strip()
            while not email_env:
                print("Email cannot be empty.")
                email_env = input(f"Enter your Email for {username}: ").strip()
            user.add_user(data_dir=DATA_ROOT, auto_user=username, auto_pass=password_env, email=email_env)
            verify.verify(username, password_env, data_dir=DATA_ROOT)
        elif action == "l":
            username = input("Enter your Username: ").strip()
            password_env = pwinput.pwinput(prompt="Enter your Password: ", mask="*")
            verify.verify(username, password_env, data_dir=DATA_ROOT)
        else:
            print("Invalid option. Exiting.")
            sys.exit(1)

    # Ensure user directories
    user_dir = os.path.join(DATA_ROOT, username)
    for subdir in ["contacts", "public_keys", "private_keys"]:
        os.makedirs(os.path.join(user_dir, subdir), exist_ok=True)

    # Start broadcasting/listening
    start_network(username)

    # Welcome message and main loop
    welcome_msg(username)
    main(username)