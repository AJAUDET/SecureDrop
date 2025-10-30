import json
import sys
import os
import pwinput
from password import create_salted_hash
from Crypto.PublicKey import RSA

# DATA_DIR will be passed from securedrop.py
DATA_DIR = "."

PUB_DIR = os.path.join(DATA_DIR, "public_keys")
PRIV_DIR = os.path.join(DATA_DIR, "private_keys")

os.makedirs(PUB_DIR, exist_ok=True)
os.makedirs(PRIV_DIR, exist_ok=True)

def add_user(data_dir=DATA_DIR):
    global DATA_DIR
    DATA_DIR = data_dir
    passwd_file = os.path.join(DATA_DIR, 'passwd.json')

    username = input("Enter your Username: ")
    email = input("Enter your Email: ")
    pwd = pwinput.pwinput(prompt="Enter your Password: ", mask='*')
    pwd2 = pwinput.pwinput(prompt="Reenter your Password: ", mask='*')

    if pwd != pwd2:
        print("Passwords do not match, try again\n")
        return

    try:
        if os.path.exists(passwd_file):
            with open(passwd_file, 'r') as f:
                data = json.load(f)
        else:
            data = {"Users": {}}

        if username in data["Users"]:
            print(f"User already registered")
            return

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

        with open(passwd_file, 'w') as f:
            json.dump(data, f, indent=2)

        keys_path = os.path.join(PUB_DIR, 'keys.json')
        if os.path.exists(keys_path):
            with open(keys_path, 'r') as f:
                pub_keys_data = json.load(f)
        else:
            pub_keys_data = {"Users": {}}

        pub_keys_data["Users"][username] = {"Public Key": public_key_str}

        with open(keys_path, 'w') as f:
            json.dump(pub_keys_data, f, indent=2)

        with open(os.path.join(PUB_DIR, f"{username}.pub"), 'w') as f:
            f.write(public_key_str)

        with open(os.path.join(PRIV_DIR, f"{username}.priv"), 'w') as f:
            f.write(private_key_str)

        print("User created successfully\n")
    except Exception as e:
        print(f"Error adding user: {type(e).__name__} - {e}")