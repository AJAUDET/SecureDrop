from datetime import datetime
import pytz

def welcome_msg(username):
    print("\n\n")
    print("------------------------------------------------------")
    print("\n\n\t\tLog in successful\t\t\n\n")
    print("------------------------------------------------------")
    print(f"\tHello {username} Welcome to Secure Drop\t\t")
    print("This program is designed to transfer files between you and your contacts, given that they are also online\n\n")
    print(f"\tLogin Date: {datetime.today().strftime('%d/%m/%Y')}")
    print(f"\tLogin Time: {datetime.now(pytz.utc).astimezone(pytz.timezone('US/Eastern')).strftime('%H:%M:%S')}")
    print(f"\n\n\tHave a secure day, {username}!")
    print(f"Enter 'help' to see a list of available commands.")
    print("------------------------------------------------------")
