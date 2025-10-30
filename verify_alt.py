import json
import sys
import pwinput
import password
import os

def verify(user, pwd, data_dir="."):
    passwd_file = os.path.join(data_dir, "passwd.json")
    with open(passwd_file, "r") as f:
        data = json.load(f)
    passwd_file = os.path.join(data_dir, 'passwd.json')

    attempts = 3
    try:
        with open(passwd_file, 'r') as f:
            data = json.load(f)
            while attempts > 0:
                if attempts == 3:
                    inp_usr = user
                    inp_pwd = pwd
                else:
                    inp_usr = input("Enter Username: ")
                    inp_pwd = pwinput.pwinput("Enter Password: ")

                if inp_usr in data["Users"]:
                    stored_hash = data["Users"][inp_usr]["Password"]
                    if password.verify_password(stored_hash, inp_pwd):
                        return inp_usr
                    else:
                        attempts -= 1
                        print(f"Username or Password is incorrect. Attempts remaining: {attempts}")
                else:
                    attempts -= 1
                    print(f"Username or Password is incorrect. Attempts remaining: {attempts}")

            print("Too many failed attempts. Exiting.")
            sys.exit(1)
    except FileNotFoundError:
        print("Authentication database not found")
        sys.exit(1)
    except json.JSONDecodeError:
        print("Authentication database corrupted")
        sys.exit(1)
    except KeyError:
        print("Authentication database missing required fields")
        sys.exit(1)
    except Exception as e:
        print(f"Authentication error occurred: {e}")
        sys.exit(1)