#   Author : AJ Audet
#   Purpose : Verify a User's login information based off of their username + salt+hashed password
#   ALT : Basis for user verification for logging in for Secure Drop

import json
import sys
import password
import pwinput

def verify(inp_usr, inp_pwd):
    try:
        with open('passwd.json', 'r') as f:
            data = json.load(f)
            if inp_usr in data["Users"]:
                stored_hash = data["Users"][inp_usr]["Password"]
                if password.verify_password(stored_hash, inp_pwd):
                    print(f"Log in successful")
                else:
                    print(f"Username or Password is incorrect")
            else:
                print(f"Username or Password is incorrect")
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
        print("Authentication error occurred")
        sys.exit(1)
        
if __name__ == "__main__":
    if (len(sys.argv) != 2):
        print(f"Usage:")
        print(f"\tpython3 verify.py --verify")
        sys.exit(1)
    mode = sys.argv[1]
    
    if mode == "--verify":
        verify()
    else:
        print(f"Improper Usage")