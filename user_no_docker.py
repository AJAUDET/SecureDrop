import os
import json
import pwinput
from password import create_salted_hash
from Crypto.PublicKey import RSA

# ----------------------------
# Host paths for Docker-free testing
# ----------------------------
DATA_DIR = "/tmp/securedrop_test/shared"
PASSWD_FILE = os.path.join(DATA_DIR, "passwd.json")

def add_user(data_dir=DATA_DIR, auto_user=None, auto_pass=None, email=None):
    username = auto_user or input("Enter your Username: ").strip()
    
    # Prompt for email if not provided
    if email is None:
        email = input(f"Enter your Email for {username}: ").strip()
        while not email:
            print("Email cannot be empty.")
            email = input(f"Enter your Email for {username}: ").strip()
    
    # Prompt for password if not provided
    pwd = auto_pass or pwinput.pwinput(prompt="Enter your Password: ", mask="*")
    if not auto_pass:
        pwd2 = pwinput.pwinput(prompt="Reenter your Password: ", mask="*")
        if pwd != pwd2:
            print("Passwords do not match, try again\n")
            return add_user(data_dir=data_dir, email=email)

    # Load or create passwd.json
    passwd_file = os.path.join(data_dir, "passwd.json")
    if os.path.exists(passwd_file):
        with open(passwd_file, "r") as f:
            try:
                data = json.load(f)
            except json.JSONDecodeError:
                data = {"Users": {}}
    else:
        data = {"Users": {}}

    if username in data["Users"]:
        print(f"User '{username}' already registered")
        return

    # Generate RSA keys
    private_key = RSA.generate(2048)
    public_key = private_key.publickey()
    private_key_str = private_key.export_key().decode("utf-8")
    public_key_str = public_key.export_key().decode("utf-8")
    pwd_hash = create_salted_hash(pwd)

    # Update passwd.json
    data["Users"][username] = {
        "Password": pwd_hash,
        "Email": email,
        "Public Key": public_key_str
    }
    os.makedirs(data_dir, exist_ok=True)
    with open(passwd_file, "w") as f:
        json.dump(data, f, indent=2)

    # Create user directories
    user_dir = os.path.join(data_dir, username)
    for sub in ["public_keys", "private_keys", "contacts"]:
        os.makedirs(os.path.join(user_dir, sub), exist_ok=True)

    # Save keys
    with open(os.path.join(user_dir, "public_keys", f"{username}.pub"), "w") as f:
        f.write(public_key_str)
    with open(os.path.join(user_dir, "private_keys", f"{username}.priv"), "w") as f:
        f.write(private_key_str)

    print(f"[INFO] User '{username}' created successfully with directories and keys.")
