#   Author : AJ Audet
#   Purpose : Implementing adding a user and their password as a hash to a file
#   ALT : Basis for how we add/verify users for Secure Drop
import json
import sys
import os
import pwinput
from password import create_salted_hash
from Crypto.PublicKey import RSA

def add_user():
    user = input("Enter a Username: ")
    pwd = pwinput.pwinput(prompt="Enter a Password: ", mask='*')
    try:
        if os.path.exists('passwd.txt'):
            with open('passwd.txt', 'r') as outF:
                data = json.load(outF)
                if "User" in data:
                    old_usr = data["User"]
                    old_pwd = data["Password"]
                    data = {
                        "Users": {
                            old_usr : old_pwd
                        }
                    }
        else:
            data = {"Users": {}}

        if user in data["Users"]:
            print(f"User already registered")
            return

        private_key = RSA.generate(2048)
        public_key = private_key.public_key()
        
        private_key_str = private_key.export_key().decode("utf-8")
        public_key_str = public_key.export_key().decode("utf-8")
        
        pwd_hash = create_salted_hash(pwd)
        data["Users"][user] = {
            "Password":pwd_hash,
            "Public Key":public_key_str
            }
        with open('passwd.txt', 'w') as outF:
            json.dump(data, outF, indent=2)

        with open(f"{user}.priv", 'w') as outF:
            data = private_key_str
            json.dump(data, outF)

        print("User created successfully")
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