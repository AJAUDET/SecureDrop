from datetime import datetime
import pytz

def welcome_msg(username):
    print("------------------------------------------------------")
    print("\n\n\t\tLog in successful\t\t\n\n")
    print("------------------------------------------------------")
    print(f"\tHello {username} Welcome to Secure Drop\t\t")
    print("\tThis program is designed to transfer files between you and your contacts, given that they are also online\n\n")
    print(f"\tLogin Date: {datetime.today().strftime("%d/%m/%Y")}")
    print(f"\tLogin Time: {datetime.now(pytz.utc).astimezone(pytz.timezone('US/Eastern')).strftime("%H:%M:%S")}")