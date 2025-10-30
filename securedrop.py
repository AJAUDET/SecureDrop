import os
import sys
import pwinput
import user_alt as user
import verify_alt as verify
from contactmanage import add_contact, list_contacts, verify_contact, admin_list, admin_clear
from network import start_network
from welcome import welcome_msg
import json

AUTH_DIR = "/app/auth"
DATA_DIR = "/app/data"

# Map commands
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
            if username == "admin":
                print("admin_list, admin_clear")
        else:
            print("Unknown command. Type 'help' for a list of commands.")

if __name__ == "__main__":
    os.makedirs(AUTH_DIR, exist_ok=True)
    os.makedirs(DATA_DIR, exist_ok=True)

    # Environment variables
    username_env = os.environ.get("USER_NAME")
    password_env = os.environ.get("USER_PASSWORD")

    # Load existing users
    passwd_file = os.path.join(AUTH_DIR, "passwd.json")
    if os.path.exists(passwd_file):
        with open(passwd_file, "r") as f:
            try:
                users_data = json.load(f)
            except json.JSONDecodeError:
                users_data = {"Users": {}}
    else:
        users_data = {"Users": {}}

    # --- Case 1: USER_NAME and USER_PASSWORD provided ---
    if username_env and password_env:
        if username_env in users_data["Users"]:
            verify.verify(username_env, password_env, auth_dir=AUTH_DIR, data_dir=DATA_DIR)
        else:
            print(f"[INFO] User '{username_env}' does not exist. Creating automatically.")
            user.add_user(auto_user=username_env, auto_pass=password_env,
                          auth_dir=AUTH_DIR, data_dir=DATA_DIR)

    # --- Case 2: Only USER_NAME provided ---
    elif username_env:
        if username_env in users_data["Users"]:
            password_env = pwinput.pwinput(f"Enter password for {username_env}: ", mask="*")
            verify.verify(username_env, password_env, auth_dir=AUTH_DIR, data_dir=DATA_DIR)
        else:
            print(f"[INFO] User '{username_env}' does not exist. Creating automatically.")
            password_env = pwinput.pwinput(f"Create password for {username_env}: ", mask="*")
            user.add_user(auto_user=username_env, auto_pass=password_env,
                          auth_dir=AUTH_DIR, data_dir=DATA_DIR)

    # --- Case 3: No environment variables, interactive login/register ---
    else:
        action = input("Do you want to (l)ogin or (r)egister? [l/r]: ").strip().lower()
        if action == "r":
            user.add_user(auth_dir=AUTH_DIR, data_dir=DATA_DIR)
            username_env = input("Enter your Username: ").strip()
            password_env = pwinput.pwinput("Enter your Password: ", mask="*")
            verify.verify(username_env, password_env, auth_dir=AUTH_DIR, data_dir=DATA_DIR)
        elif action == "l":
            username_env = input("Enter your Username: ").strip()
            password_env = pwinput.pwinput("Enter your Password: ", mask="*")
            verify.verify(username_env, password_env, auth_dir=AUTH_DIR, data_dir=DATA_DIR)
        else:
            print("Invalid option. Exiting.")
            sys.exit(1)

    # Start network and main loop
    start_network(username_env)
    welcome_msg(username_env)
    main(username_env)