import os
import json
import pwinput
from password import create_salted_hash
from Crypto.PublicKey import RSA

def add_user(data_dir="/app/data", auto_user=None, auto_pass=None):
    pub_dir = os.path.join(data_dir, "public_keys")
    priv_dir = os.path.join(data_dir, "private_keys")
    os.makedirs(pub_dir, exist_ok=True)
    os.makedirs(priv_dir, exist_ok=True)

    passwd_file = os.path.join(data_dir, "passwd.json")

    if auto_user and auto_pass:
        username = auto_user
        pwd = auto_pass
        email = ""
    else:
        username = input("Enter your Username: ").strip()
        email = input("Enter your Email: ").strip()
        pwd = pwinput.pwinput(prompt="Enter your Password: ", mask="*")
        pwd2 = pwinput.pwinput(prompt="Reenter your Password: ", mask="*")
        if pwd != pwd2:
            print("Passwords do not match, try again\n")
            return

    # Load existing users
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

    # Generate RSA keys
    private_key = RSA.generate(2048)
    public_key = private_key.publickey()
    private_key_str = private_key.export_key().decode("utf-8")
    public_key_str = public_key.export_key().decode("utf-8")

    pwd_hash = create_salted_hash(pwd)

    data["Users"][username] = {
        "Password": pwd_hash,
        "Email": email,
        "Public Key": public_key_str
    }

    with open(passwd_file, "w") as f:
        json.dump(data, f, indent=2)

    with open(os.path.join(pub_dir, f"{username}.pub"), "w") as f:
        f.write(public_key_str)
    with open(os.path.join(priv_dir, f"{username}.priv"), "w") as f:
        f.write(private_key_str)

    print(f"[+] User '{username}' created successfully")
