import json
import os
import password


def add_user(data_dir="/app/data", auto_user=None, auto_pass=None):
    """
    Adds a new user interactively or automatically.
    - data_dir: isolated directory (volume)
    - auto_user / auto_pass: non-interactive creation for Docker automation
    """
    passwd_file = os.path.join(data_dir, "passwd.json")

    # Load or initialize JSON structure
    if os.path.exists(passwd_file):
        with open(passwd_file, "r") as f:
            data = json.load(f)
    else:
        data = {"Users": {}}

    # Gather credentials
    if auto_user and auto_pass:
        username = auto_user
        password_plain = auto_pass
    else:
        username = input("Enter a new Username: ").strip()
        password_plain = password.get_password_input()

    # Check if user exists
    if username in data["Users"]:
        print(f"User '{username}' already exists.")
        return

    # Hash the password
    hashed_pw = password.hash_password(password_plain)

    # Create user directory
    user_dir = os.path.join(data_dir, username)
    os.makedirs(user_dir, exist_ok=True)

    # Save user data
    data["Users"][username] = {"Password": hashed_pw}
    with open(passwd_file, "w") as f:
        json.dump(data, f, indent=4)

    print(f"✅ User '{username}' registered successfully in isolated data volume.")