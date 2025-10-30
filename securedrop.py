import os
import sys
import pwinput
import user_alt as user
import verify_alt as verify
from contactmanage import add_contact, list_contacts, verify_contact, admin_list, admin_clear
from network import start_network
from welcome import welcome_msg

DATA_DIR = "/app/data"

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
    username = os.environ.get("USER_NAME")
    password_env = os.environ.get("USER_PASSWORD")

    # Auto-create user if USER_NAME is provided
    if username:
        user.add_user(data_dir=DATA_DIR, auto_user=username, auto_pass=password_env)
    else:
        login = input("Would you like to register (y/n): ").strip()
        if login.lower() == "y":
            user.add_user(data_dir=DATA_DIR)

        username = input("Enter your Username: ").strip()
        password_env = pwinput.pwinput(prompt="Enter your Password: ", mask="*")

    # Verify login
    verify.verify(username, password_env, data_dir=DATA_DIR)

    # Start network
    start_network(username)

    # Welcome message
    welcome_msg(username)

    # Main command loop
    main(username)