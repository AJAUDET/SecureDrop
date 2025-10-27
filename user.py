#   Author : AJ Audet
#   Purpose : Implementing adding a user and their password as a hash to a file
#   ALT : Basis for how we add/verify users for Secure Drop
import json
import sys
import os
import pwinput
from password import create_salted_hash
from Crypto.PublicKey import RSA

PUB_DIR = "public_keys"
PRIV_DIR = "private_keys"

if not os.path.exists(PUB_DIR):
    os.makedirs(PUB_DIR)
if not os.path.exists(PRIV_DIR):
    os.makedirs(PRIV_DIR)

def add_user():
    username = input("Enter your Username: ")
    email = input("Enter your Email: ")
    pwd = pwinput.pwinput(prompt="Enter your Password: ", mask='*')
    pwd2 = pwinput.pwinput(prompt="Reenter your Password: ", mask='*')
    if(pwd != pwd2):
        print("Passwords do not match, try again\n")
    try:
        if os.path.exists('passwd.json'):
            with open('passwd.json', 'r') as outF:
                data = json.load(outF)
                if "User" in data:
                    old_usr = data["User"]
                    old_pwd = data["Password"]
                    data = {
                        "Users": {
                            old_usr : {
                                "Password":old_pwd,
                                "Email":"",
                                "Public Key":""
                            }
                        }
                    }
        else:
            data = {"Users": {}}

        if username in data["Users"]:
            print(f"User already registered")
            return

        private_key = RSA.generate(2048)
        public_key = private_key.public_key()
        
        private_key_str = private_key.export_key().decode("utf-8")
        public_key_str = public_key.export_key().decode("utf-8")
        
        pwd_hash = create_salted_hash(pwd)
        
        data["Users"][username] = {
            "Password": pwd_hash,
            "Email": email,
            "Public Key": public_key_str
            }
        with open('passwd.json', 'w') as outF:
            json.dump(data, outF, indent=2)
            
        with open(os.path.join(PUB_DIR, 'keys.json'), 'w') as outF:
            data["Users"][username] = {
                "Public Key": public_key_str
            }
            json.dump(data, outF, indent=2)

        with open(os.path.join(PUB_DIR, f"{username}.pub"), 'w') as outF:
            data = public_key_str
            print(f"{data}", file=outF)

        with open(os.path.join(PRIV_DIR, f"{username}.priv"), 'w') as outF:
            data = private_key_str
            print(f"{data}", file=outF)

        print("User created successfully\n")
    except json.JSONDecodeError:
        print("Error: Corrupted database file")
    except PermissionError:
        print("Error: No permission to write to file")
    except Exception as e:
        print(f"Error adding user: {type(e).__name__}")
          

if __name__ == "__main__":
    if (len(sys.argv) != 2):
        print(f"Usage:")
        print(f"\tpython3 add_user.py --add <outFile>")
        sys.exit(1)
    mode = sys.argv[1]
    
    if mode == '--add':
        add_user()
    else:
        print(f"Improper Usage")