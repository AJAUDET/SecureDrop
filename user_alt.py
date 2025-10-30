import json, os, pwinput
from password import create_salted_hash
from Crypto.PublicKey import RSA

def add_user(username=None, email=None, password=None, data_dir="/app/data"):
    PUB_DIR = os.path.join(data_dir, "public_keys")
    PRIV_DIR = os.path.join(data_dir, "private_keys")
    os.makedirs(PUB_DIR, exist_ok=True)
    os.makedirs(PRIV_DIR, exist_ok=True)

    if username is None:
        username = input("Enter your Username: ")
    if email is None:
        email = input("Enter your Email: ")
    if password is None:
        password = pwinput.pwinput(prompt="Enter your Password: ", mask='*')
        password2 = pwinput.pwinput(prompt="Reenter your Password: ", mask='*')
        if password != password2:
            print("Passwords do not match")
            return

    passwd_file = os.path.join(data_dir, "passwd.json")
    if os.path.exists(passwd_file):
        with open(passwd_file, "r") as f:
            data = json.load(f)
    else:
        data = {"Users": {}}

    if username in data["Users"]:
        print("User already registered")
        return

    private_key = RSA.generate(2048)
    public_key = private_key.public_key()
    pwd_hash = create_salted_hash(password)

    data["Users"][username] = {
        "Password": pwd_hash,
        "Email": email,
        "Public Key": public_key.export_key().decode()
    }

    with open(passwd_file, "w") as f:
        json.dump(data, f, indent=2)

    with open(os.path.join(PUB_DIR, f"{username}.pub"), "w") as f:
        f.write(public_key.export_key().decode())
    with open(os.path.join(PRIV_DIR, f"{username}.priv"), "w") as f:
        f.write(private_key.export_key().decode())

    print(f"User {username} created successfully")