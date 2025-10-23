import verify
import pwinput
import user
from contactmanage import add_contact, list_contacts, verify_contact, admin_list, admin_clear
import sys


command_map = {
    "add": add_contact,
    "list": list_contacts,
    "verify": verify_contact,
    "admin_list": admin_list,
    "admin_clear": admin_clear,
    "exit": lambda username: sys.exit(0)
}


def main(username):
    print(f"Welcome to Secure Drop, {username}!")
    print("Enter 'help' for a list of commands, when done enter 'exit'")
    while True:
        cmd = input("$: ").strip()
        if cmd in command_map:
            command_map[cmd](username)  
        elif cmd == "help":
            print("Available commands: ")
            print("add - Add a new contact")
            print("list - List all contacts")
            print("verify - Verify a contact's identity")
            print("admin_list - View all users’ contacts (admin only)")
            print("admin_clear - Clear the master contact log (admin only)")
            print("exit - Exit SecureDrop")
        else:
            print("Unknown command. Type 'help' for a list of commands.")

if __name__ == '__main__':
    login = input("Would you like to register (y/n): ").strip()
    if login.lower() == 'y':
        user.add_user()
    username = input("Enter Username: ")
    pwd = pwinput.pwinput(prompt="Enter your Password: ", mask='*')
    username = verify.verify(username, pwd) 
    main(username)  