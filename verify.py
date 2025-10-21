#   Author : AJ Audet
#   Purpose : Verify a User's login information based off of their username + salt+hashed password
#   ALT : Basis for user verification for logging in for Secure Drop

import json
import sys
import password

def verify():
    try:
        inp_user = input("Enter Username: ")
        inp_pwd = input("Enter Password: ")
        with open('passwd.id', 'r') as f:
            data = json.load(f)
            if inp_user in data["Users"]:
                stored_hash = data["Users"][inp_user]
                if password.verify_password(stored_hash, inp_pwd):
                    print(f"Log in successful")
                else:
                    print(f"Username or Password is incorrect")
            else:
                print(f"Username or Password is incorrect")
    except FileNotFoundError:
        print("Authentication database not found")
    except json.JSONDecodeError:
        print("Authentication database corrupted")
    except KeyError:
        print("Authentication database missing required fields")
    except Exception as e:
        print("Authentication error occurred")
        
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