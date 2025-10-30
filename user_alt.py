import os
import json
import pwinput
from password import create_salted_hash
from Crypto.PublicKey import RSA

PASSWD_FILE = "passwd.json"  # Path passed from securedrop.py
DATA_DIR = "/app/data"       # Root data directory

def add_user(data_dir=DATA_DIR, auto_user=None, auto_pass=None):
    username = auto_user or input("Enter your Username: ").strip()
    email = input("Enter your Email: ").strip() if not auto_user else ""
    pwd = auto_pass or pwinput.pwinput(prompt="Enter your Password: ", mask="*")
    if not auto_pass:
        pwd2 = pwinput.pwinput(prompt="Reenter your Password: ", mask="*")
        if pwd != pwd2:
            print("Passwords do not match, try again\n")
            return add_user(data_dir=data_dir)

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
        print(f"User already registered")
        return

    # Generate keys
    private_key = RSA.generate(2048)
    public_key = private_key.publickey()
    private_key_str = private_key.export_key().decode("utf-8")
    public_key_str = public_key.export_key().decode("utf-8")
    pwd_hash = create_salted_hash(pwd)

    # Update passwd.json
    data["Users"][username] = {"Password": pwd_hash, "Email": email, "Public Key": public_key_str}
    with open(passwd_file, "w") as f:
        json.dump(data, f, indent=2)

    # Create user directories
    user_dir = os.path.join(data_dir, username)
    pub_dir = os.path.join(user_dir, "public_keys")
    priv_dir = os.path.join(user_dir, "private_keys")
    contacts_dir = os.path.join(user_dir, "contacts")
    for d in [pub_dir, priv_dir, contacts_dir]:
        os.makedirs(d, exist_ok=True)

    # Save keys
    with open(os.path.join(pub_dir, f"{username}.pub"), "w") as f:
        f.write(public_key_str)
    with open(os.path.join(priv_dir, f"{username}.priv"), "w") as f:
        f.write(private_key_str)

    print(f"User '{username}' created successfully with directories and keys.")