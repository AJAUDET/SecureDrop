import os
import sys
import json
import pwinput
import password

def verify(user, pwd, auth_dir="/app/auth", data_dir="/app/data"):
    passwd_file = os.path.join(auth_dir, "passwd.json")
    if not os.path.exists(passwd_file):
        print(f"[INFO] {passwd_file} not found. Creating empty authentication database.")
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
            data = json.load(f)

        if inp_usr in data["Users"]:
            stored_hash = data["Users"][inp_usr]["Password"]
            if password.verify_password(stored_hash, inp_pwd):
                # Ensure user directories exist
                user_dir = os.path.join(data_dir, inp_usr)
                for subdir in ["contacts", "public_keys", "private_keys"]:
                    os.makedirs(os.path.join(user_dir, subdir), exist_ok=True)
                print(f"Login successful for {inp_usr}")
                return inp_usr
            else:
                attempts -= 1
                print(f"Incorrect credentials. Attempts remaining: {attempts}")
        else:
            attempts -= 1
            print(f"Incorrect credentials. Attempts remaining: {attempts}")

    print("Too many failed attempts. Exiting.")
    sys.exit(1)