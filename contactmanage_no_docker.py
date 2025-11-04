import os
import json
import threading
import time

# ----------------------------
# Host-local paths for Docker-free testing
# ----------------------------
DATA_DIR = "/tmp/securedrop_test/shared"
CONTACTS_DIR = os.path.join(DATA_DIR, "contacts")
MASTER_CONTACTS_FILE = os.path.join(CONTACTS_DIR, "admin_master_contacts.json")
DISCOVERY_FILE = os.path.join(DATA_DIR, "discovered_users.json")

file_lock = threading.Lock()

# Ensure directories exist
os.makedirs(CONTACTS_DIR, exist_ok=True)
if not os.path.exists(MASTER_CONTACTS_FILE):
    with open(MASTER_CONTACTS_FILE, "w") as f:
        json.dump({}, f, indent=4)


def get_user_contacts_file(username):
    return os.path.join(CONTACTS_DIR, f"{username}.json")


def add_contact(username):
    contacts_file = get_user_contacts_file(username)

    if not os.path.exists(contacts_file):
        with open(contacts_file, "w") as f:
            json.dump({}, f, indent=4)

    with open(contacts_file, "r") as f:
        contacts = json.load(f)

    contact_username = input("Enter the username of the contact: ").strip()
    contact_full_name = input("Enter the full name of the contact: ").strip()
    contact_email = input("Enter the email of the contact: ").strip()

    if contact_username in contacts:
        print(f"{contact_username} is already in your contacts.")
        return

    contacts[contact_username] = {
        "full_name": contact_full_name,
        "email": contact_email
    }

    # Save user contacts
    with open(contacts_file, "w") as f:
        json.dump(contacts, f, indent=4)
    print(f"Contact '{contact_username}' added successfully to your personal contacts.")

    # Update master contact file
    with open(MASTER_CONTACTS_FILE, "r") as f:
        master_contacts = json.load(f)

    master_contacts[f"{username}:{contact_username}"] = {
        "added_by": username,
        "contact_full_name": contact_full_name,
        "contact_email": contact_email
    }

    with open(MASTER_CONTACTS_FILE, "w") as f:
        json.dump(master_contacts, f, indent=4)

    # Update discovery file if contact is online
    if os.path.exists(DISCOVERY_FILE):
        try:
            with open(DISCOVERY_FILE, "r") as f:
                discovered = json.load(f)
        except json.JSONDecodeError:
            discovered = {}
        if contact_username in discovered:
            discovered[contact_username]["mutual_contact"] = True
            with open(DISCOVERY_FILE, "w") as f:
                json.dump(discovered, f, indent=2)


def remove_contact(username):
    contacts_file = get_user_contacts_file(username)
    with file_lock:
        if not os.path.exists(contacts_file):
            print("No contacts to remove.")
            return

        with open(contacts_file, "r") as f:
            contacts = json.load(f)

        if not contacts:
            print("Contact list is empty.")
            return

        contact_username = input("Enter the username of the contact to remove: ").strip()
        if contact_username not in contacts:
            print(f"Contact '{contact_username}' not found.")
            return

        confirm = input(f"Remove '{contact_username}'? (y/n): ").strip().lower()
        if confirm != "y":
            print("Cancelled.")
            return

        del contacts[contact_username]

        with open(contacts_file, "w") as f:
            json.dump(contacts, f, indent=4)

        # Remove from master log
        if os.path.exists(MASTER_CONTACTS_FILE):
            with open(MASTER_CONTACTS_FILE, "r") as f:
                master_contacts = json.load(f)
            key = f"{username}:{contact_username}"
            if key in master_contacts:
                del master_contacts[key]
                with open(MASTER_CONTACTS_FILE, "w") as f:
                    json.dump(master_contacts, f, indent=4)

        print(f"Contact '{contact_username}' removed.")


def list_contacts(username):
    contacts_file = get_user_contacts_file(username)
    if not os.path.exists(contacts_file):
        print("You have no contacts.")
        return

    with open(contacts_file, "r") as f:
        contacts = json.load(f)

    # Get online users from discovery file
    online_data = {}
    if os.path.exists(DISCOVERY_FILE):
        try:
            with open(DISCOVERY_FILE, "r") as f:
                online_data = json.load(f)
        except json.JSONDecodeError:
            online_data = {}

    mutual_online = []
    for contact_username in contacts:
        contact_file = get_user_contacts_file(contact_username)
        if not os.path.exists(contact_file):
            continue
        with open(contact_file, "r") as f:
            their_contacts = json.load(f)
        if username in their_contacts and contact_username in online_data:
            mutual_online.append((contact_username, online_data[contact_username]["last_seen"]))

    if not mutual_online:
        print("No contacts currently online.")
    else:
        print("The following contacts are online (last seen timestamp):")
        for user_name, last_seen in mutual_online:
            details = contacts[user_name]
            last_seen_str = time.strftime("%Y-%m-%d %H:%M:%S", time.localtime(last_seen))
            print(f"* {user_name}: {details['full_name']} ({details['email']}) - Last seen: {last_seen_str}")


def verify_contact(username):
    contacts_file = get_user_contacts_file(username)
    if not os.path.exists(contacts_file):
        print("No contacts found.")
        return

    with open(contacts_file, "r") as f:
        contacts = json.load(f)

    contact_username = input("Enter username to verify: ").strip()
    if contact_username in contacts:
        print(f"Contact '{contact_username}':")
        print(f"Full Name: {contacts[contact_username]['full_name']}")
        print(f"Email: {contacts[contact_username]['email']}")
    else:
        print(f"Contact '{contact_username}' not found.")


def admin_list(admin_username):
    if admin_username.lower() != "admin":
        print("Access denied.")
        return

    with open(MASTER_CONTACTS_FILE, "r") as f:
        master_contacts = json.load(f)

    if not master_contacts:
        print("No contacts recorded.")
        return

    print("Master Contact Log:")
    for key, details in master_contacts.items():
        print(f"- {key} | Added by: {details['added_by']} | {details['contact_full_name']} ({details['contact_email']})")


def admin_clear(admin_username):
    if admin_username.lower() != "admin":
        print("Access denied.")
        return

    confirm = input("Clear master contact log? (y/n): ").strip().lower()
    if confirm != "y":
        print("Cancelled.")
        return

    with open(MASTER_CONTACTS_FILE, "w") as f:
        json.dump({}, f, indent=4)
    print("Master contact log cleared.")