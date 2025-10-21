#   Author : AJ Audet
#   Purpose : Implementing adding a user and their password as a hash to a file
#   ALT : Basis for how we add/verify users for Secure Drop

import json
import sys
from password import create_salted_hash

def add_user(outFile): 
    try:
        with open(outFile, 'x') as outF:
            user = input("Enter a Username: ")
            pswd = input("Enter a Password: ")
            data = {"User: ": user, "Password: ": create_salted_hash(pswd)}
            print(json.dumps(data, separators=(',', ':')), file=outF)
    except:
        with open(outFile, 'a+') as outF:
            user = input("Enter a Username: ")
            pswd = input("Enter a Password: ")
            data = {"User: ": user, "Password: ": create_salted_hash(pswd)}
            print(json.dumps(data, separators=(',', ':')), file=outF)

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