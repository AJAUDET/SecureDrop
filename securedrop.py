import user
import verify
import pwinput
from commands import add, helpu, listc
import sys


# user creation prompt at the start 
# if y: create new user
# if n: login to existing account

command_map = {
    "add": add,
    "help": helpu,
    "list": listc,
    "exit": lambda: sys.exit(0)
}

def main():
    print("Welcome to Secure Drop, {user}".format(user=user))
    print("Enter 'help' for a list of commands, when done enter 'exit'")
    print("Enter a Command to start")
    cmd = ""
    while cmd != "exit":
        cmd = input("$: ").strip()
        if cmd in command_map:
            command_map[cmd]()
        else:
            print("Unknown command. Type 'help' for a list of commands")

if __name__ == '__main__':
    login = input("Would you like to register (y/n): ").strip()
    if (login.lower() == 'y'):  user.add_user()
    user = input("Enter Username: ")
    pwd = pwinput.pwinput(prompt="Enter your Password: ", mask='*')
    verify.verify(user, pwd)
    main()