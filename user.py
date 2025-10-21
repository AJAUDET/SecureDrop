#   Author : AJ Audet
#   Purpose : Implementing adding a user and their password as a hash to a file
#   ALT : Basis for how we add/verify users for Secure Drop

import json
import sys
import os
from password import create_salted_hash

def add_user(outFile):
    user = input("Enter a Username: ")
    pwd = input("Enter a Password: ")
    try:
        if os.path.exists(outFile):
            with open(outFile, 'r') as outF:
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

        pwd_hash = create_salted_hash(pwd)
        data["Users"][user] = pwd_hash
        with open(outFile, 'w') as outF:
            json.dump(data, outF, indent=2)
    except json.JSONDecodeError:
        print("Error: Corrupted database file")
    except PermissionError:
        print("Error: No permission to write to file")
    except Exception as e:
        print(f"Error adding user: {type(e).__name__}")
          

if __name__ == "__main__":
    if (len(sys.argv) != 3):
        print(f"Usage:")
        print(f"\tpython3 add_user.py --add <outFile>")
        sys.exit(1)
    mode = sys.argv[1]
    pwd_file = sys.argv[2]
    
    if mode == '--add':
        add_user(pwd_file)
    else:
        print(f"Improper Usage")