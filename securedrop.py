import os
import sys
import pwinput
import verify_alt as verify
import user as user
from contactmanage_alt import add_contact, list_contacts, verify_contact, admin_list, admin_clear
from network import start_network
from welcome import welcome_msg

# --- Volume root for this user ---
DATA_DIR = "/app/data"

# Command map
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
    """Interactive shell for the user inside the container"""
    while True:
        cmd = input(f"{username}@securedrop.com: ").strip()
        if cmd in command_map:
            command_map[cmd](username)
        elif cmd == "help":
            print("Available commands:")
            print("add - Add a new contact")
            print("list - List all contacts")
            print("verify - Verify a contact's identity")
            print("clear - Clears the terminal")
            print("exit - Exit SecureDrop")
            if username == 'admin':
                print("admin_list - View all users’ contacts (admin only)")
                print("admin_clear - Clear the master contact log (admin only)")
        else:
            print("Unknown command. Type 'help' for a list of commands.")


if __name__ == "__main__":
    # Ensure data directory exists inside the volume
    os.makedirs(DATA_DIR, exist_ok=True)

    # Get user info from environment variables
    username = os.getenv("USER_NAME")
    password_env = os.getenv("USER_PASSWORD")

    if not username:
        print("Error: USER_NAME environment variable not set.")
        sys.exit(1)

    # Auto-register if user doesn’t exist yet
    passwd_file = os.path.join(DATA_DIR, "passwd.json")
    if not os.path.exists(passwd_file):
        print(f"Initializing new SecureDrop volume for user '{username}'")
        user.add_user(data_dir=DATA_DIR, auto_user=username, auto_pass=password_env)
    else:
        print(f"Using existing SecureDrop data for '{username}'")

    # Verify user (uses verify_alt, volume-aware)
    verify.verify(username, password_env, data_dir=DATA_DIR)

    # Start networking
    start_network(username)

    # Display welcome message
    welcome_msg(username)

    # Enter main CLI loop
    main(username)