import os
import json
import pwinput
from password import create_salted_hash
from Crypto.PublicKey import RSA

def add_user(auto_user=None, auto_pass=None, auth_dir="/app/auth", data_dir="/app/data"):
    os.makedirs(auth_dir, exist_ok=True)
    os.makedirs(data_dir, exist_ok=True)

    passwd_file = os.path.join(auth_dir, "passwd.json")
    if os.path.exists(passwd_file):
        with open(passwd_file, "r") as f:
            try:
                users_data = json.load(f)
            except json.JSONDecodeError:
                users_data = {"Users": {}}
    else:
        users_data = {"Users": {}}

    username = auto_user or input("Enter your Username: ").strip()
    email = input("Enter your Email: ").strip()
    pwd = auto_pass or pwinput.pwinput(prompt="Enter your Password: ", mask="*")
    if not auto_pass:
        pwd2 = pwinput.pwinput(prompt="Reenter your Password: ", mask="*")
        if pwd != pwd2:
            print("Passwords do not match, try again")
            return

    if username in users_data["Users"]:
        print(f"User {username} already exists.")
        return

    # Generate keys
    private_key = RSA.generate(2048)
    public_key = private_key.publickey()
    private_key_str = private_key.export_key().decode("utf-8")
    public_key_str = public_key.export_key().decode("utf-8")

    pwd_hash = create_salted_hash(pwd)
    users_data["Users"][username] = {"Password": pwd_hash, "Email": email, "Public Key": public_key_str}

    # Save passwd.json
    with open(passwd_file, "w") as f:
        json.dump(users_data, f, indent=2)

    # Create user directories
    user_dir = os.path.join(data_dir, username)
    for subdir in ["contacts", "public_keys", "private_keys"]:
        os.makedirs(os.path.join(user_dir, subdir), exist_ok=True)

    # Save keys inside user directories
    pub_path = os.path.join(user_dir, "public_keys", f"{username}.pub")
    priv_path = os.path.join(user_dir, "private_keys", f"{username}.priv")
    with open(pub_path, "w") as f:
        f.write(public_key_str)
    with open(priv_path, "w") as f:
        f.write(private_key_str)

    print(f"User {username} created successfully with keys at {user_dir}")