import os
import sys
import json
import pwinput
import password

def verify(user, pwd, data_dir="/app/data"):
    passwd_file = os.path.join(data_dir, "passwd.json")

    if not os.path.exists(passwd_file):
        print(f"[INFO] {passwd_file} not found, creating empty authentication database.")
        os.makedirs(data_dir, exist_ok=True)
        with open(passwd_file, "w") as f:
            json.dump({"Users": {}}, f)

    attempts = 3
    while attempts > 0:
        if attempts == 3:
            inp_usr = user
            inp_pwd = pwd
        else:
            inp_usr = input("Enter Username: ").strip()
            inp_pwd = pwinput.pwinput("Enter Password: ", mask="*")

        with open(passwd_file, "r") as f:
            try:
                data = json.load(f)
            except json.JSONDecodeError:
                data = {"Users": {}}

        if inp_usr in data["Users"]:
            stored_hash = data["Users"][inp_usr]["Password"]
            if password.verify_password(stored_hash, inp_pwd):
                print(f"Login successful: {inp_usr}")
                return inp_usr
            else:
                attempts -= 1
                print(f"Incorrect password. Attempts remaining: {attempts}")
        else:
            attempts -= 1
            print(f"Username not found. Attempts remaining: {attempts}")

    print("Too many failed attempts. Exiting.")
    sys.exit(1)