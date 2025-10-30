import verify_alt
import pwinput
import user_alt
import os
from contactmanage_alt import add_contact, list_contacts, verify_contact, admin_list, admin_clear
from network import start_network
from welcome import welcome_msg
import sys

# ------------------------------
# Use environment variable or default to /app/data
DATA_DIR = os.environ.get("DATA_DIR", "/app/data")
os.makedirs(DATA_DIR, exist_ok=True)

# Update user.py to write/read inside container volume
user_alt.DATA_DIR = DATA_DIR

# Patch contactmanage.py functions to use DATA_DIR
add_contact.DATA_DIR = DATA_DIR
list_contacts.DATA_DIR = DATA_DIR
verify_contact.DATA_DIR = DATA_DIR
admin_list.DATA_DIR = DATA_DIR
admin_clear.DATA_DIR = DATA_DIR

# Command mapping
command_map = {
    "add": add_contact,
    "list": list_contacts,
    "verify": verify_contact,
    "admin_list": admin_list,
    "admin_clear": admin_clear,
    "clear": lambda _: os.system('clear'),
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
            print("Unknown command. Type 'help' for commands.")

if __name__ == '__main__':
    env_user = os.environ.get("USER_NAME")
    env_email = os.environ.get("USER_EMAIL")
    env_password = os.environ.get("USER_PASSWORD")

    if env_user and env_email and env_password:
        # Auto-register user if not present
        user_alt.add_user(username=env_user, email=env_email, password=env_password, data_dir=DATA_DIR)
        username = env_user
        pwd = env_password
    else:
        # Interactive registration
        login = input("Would you like to register (y/n): ").strip()
        if login.lower() == "y":
            user_alt.add_user(data_dir=DATA_DIR)
        username = input("Enter your Username: ").strip()
        pwd = pwinput.pwinput(prompt="Enter your Password: ", mask='*')

    # Verify credentials
    verify_alt.verify(username, pwd, data_dir=DATA_DIR)

    # Start network broadcast/listen
    start_network(username)

    # Welcome message
    welcome_msg(username)

    # Start command loop
    main(username)
