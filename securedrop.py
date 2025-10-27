import verify
import pwinput
import user
import os
from contactmanage import add_contact, list_contacts, verify_contact, admin_list, admin_clear
from network import start_network
from welcome import welcome_msg
import sys

command_map = {
    "add": add_contact,
    "list": list_contacts,
    "verify": verify_contact,
    "admin_list": admin_list,
    "admin_clear": admin_clear,
    "clear": lambda clear: os.system('clear'),
    "exit": lambda username: sys.exit(0)
}

def main(username):
    while True:
        cmd = input(f"{username}: ").strip()
        if cmd in command_map:
            command_map[cmd](username)  
        elif cmd == "help":
            print("Available commands: ")
            print("add - Add a new contact")
            print("list - List all contacts")
            print("verify - Verify a contact's identity")
            print("clear - Clears the terminal of previous commands")
            print("exit - Exit SecureDrop")
            if username == 'admin':
                print("admin_list - View all users’ contacts (admin only)")
                print("admin_clear - Clear the master contact log (admin only)")
        else:
            print("Unknown command. Type 'help' for a list of commands.")

if __name__ == '__main__':
    login = input("Would you like to register (y/n): ").strip()
    if login.lower() == 'y':
        user.add_user()
    username = input("Enter Username: ").strip()
    pwd = pwinput.pwinput(prompt="Enter your Password: ", mask='*')
    verify.verify(username, pwd)

    start_network(username)  #startbroadcast/listen for users
   
    welcome_msg(username)           # welcome users
    
    main(username)
