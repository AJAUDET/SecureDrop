import os
import sys
import pwinput
import user
import verify
from contactmanage import add_contact, list_contacts, verify_contact, admin_list, admin_clear
from network import start_network
from welcome import welcome_msg

command_map = {
    "add": add_contact,
    "list": list_contacts,
    "verify": verify_contact,
    "admin_list": admin_list,
    "admin_clear": admin_clear,
    "clear": lambda _: os.system("clear"),
    "exit": lambda _: sys.exit(0)
}

def main(username):
    while True:
        cmd = input(f"{username}@securedrop.com: ").strip()
        if cmd in command_map:
            command_map[cmd](username)
        elif cmd == "help":
            print("Available commands: add, list, verify, clear, exit")
            if username.lower() == "admin":
                print("admin_list, admin_clear")
        else:
            print("Unknown command. Type 'help' for a list of commands.")

if __name__ == "__main__":

    mode = input("Would you like to (l)ogin, (r)egister, or (e)xit: ")

    if mode == 'l':
        username = input("Enter your Username: ")
        password = pwinput.pwinput(prompt="Enter your Password: ", mask='*')
        verify.verify(username, password)
        
        # Start broadcasting/listening
        start_network(username)

        # Welcome message and main loop
        welcome_msg(username)
        main(username)
    elif mode == 'r':
        username = user.add_user()
        start_network(username)

        # Welcome message and main loop
        welcome_msg(username)
        main(username)
    else:
        print("\tThank you for using secure drop!")
        print("\tHave a wonderful day!")
        sys.exit(0)