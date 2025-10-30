from datetime import datetime
import pytz
import pyfiglet as figlet

PROGRAM_NAME = "Secure Drop"
FONT = figlet.Figlet(font='utopiab')

# --- I want to use this in the future probs ---
ART = """
                      .;;,
 .,.               .,;;;;;,
;;;;;;;,,        ,;;%%%%%;;
 `;;;%%%%;;,.  ,;;%%;;%%%;;
   `;%%;;%%%;;,;;%%%%%%%;;'
     `;;%%;;%:,;%%%%%;;%%;;,
        `;;%%%,;%%%%%%%%%;;;
           `;:%%%%%%;;%%;;;'
              .:::::::.
                   s.
"""


def welcome_msg(username):
    print("\n\n")
    print("-----------------------------------------------------------------------------------------------")
    print(FONT.renderText(PROGRAM_NAME))
    print("-----------------------------------------------------------------------------------------------")
    print(f"\tHello {username} Welcome to Secure Drop\t\t")
    print("\tThis program is designed to transfer files between you and your contacts, given that they are also online\n\n")
    print(f"\tLogin Date: {datetime.today().strftime('%d/%m/%Y')}")
    print(f"\tLogin Time: {datetime.now(pytz.utc).astimezone(pytz.timezone('US/Eastern')).strftime('%H:%M:%S')}")
    print(f"\n\n\tHave a secure day, {username}!")
    print(f"\tEnter 'help' to see a list of available commands.")
    print("------------------------------------------------------")
    


if __name__ == "__main__":
    username = 'test'
    welcome_msg(username)