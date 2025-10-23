import os
import json

CONTACTS_DIR = "contacts"


if not os.path.exists(CONTACTS_DIR):
    os.makedirs(CONTACTS_DIR)

def get_user_contacts_file(username):
    return os.path.join(CONTACTS_DIR, f"{username}.json")

def add_contact(username):
    contacts_file = get_user_contacts_file(username)
    if not os.path.exists(contacts_file):
        with open(contacts_file, "w") as f:
            json.dump({}, f)  

    with open(contacts_file, "r") as f:
        contacts = json.load(f)

    contact_username = input("Enter the username of the contact: ")
    contact_full_name = input("Enter the full name of the contact: ")
    contact_email = input("Enter the email of the contact: ")

    if contact_username in contacts:
        print(f"{contact_username} is already in your contacts.")
    else:
        contacts[contact_username] = {
            "full_name": contact_full_name,
            "email": contact_email
        }
        with open(contacts_file, "w") as f:
            json.dump(contacts, f, indent=4)
        print(f"Contact {contact_username} added successfully.")

def list_contacts(username):
    contacts_file = get_user_contacts_file(username)
    if not os.path.exists(contacts_file):
        print("You have no contacts.")
        return

    with open(contacts_file, "r") as f:
        contacts = json.load(f)

    if not contacts:
        print("You have no contacts.")
    else:
        print("Your contacts:")
        for contact_username, details in contacts.items():
            print(f"- {contact_username}: {details['full_name']} ({details['email']})")

def verify_contact(username):
    contacts_file = get_user_contacts_file(username)
    if not os.path.exists(contacts_file):
        print("You have no contacts.")
        return

    with open(contacts_file, "r") as f:
        contacts = json.load(f)

    contact_username = input("Enter the username of the contact to verify: ")
    if contact_username in contacts:
        print(f"Contact {contact_username} exists.")
        print(f"Full Name: {contacts[contact_username]['full_name']}")
        print(f"Email: {contacts[contact_username]['email']}")
    else:
        print(f"Contact {contact_username} does not exist.")