import json
import os

def get_contacts_file(data_dir, username):
    """Return per-user contact file path."""
    os.makedirs(os.path.join(data_dir, username), exist_ok=True)
    return os.path.join(data_dir, username, f"{username}_contacts.json")


def add_contact(username, data_dir="/app/data"):
    """Add a new contact for the current user."""
    contacts_file = get_contacts_file(data_dir, username)

    contact_name = input("Enter contact name: ").strip()
    contact_info = input("Enter contact info: ").strip()

    contacts = {}
    if os.path.exists(contacts_file):
        with open(contacts_file, "r") as f:
            contacts = json.load(f)

    contacts[contact_name] = contact_info

    with open(contacts_file, "w") as f:
        json.dump(contacts, f, indent=4)

    print(f"Contact '{contact_name}' added successfully.")


def list_contacts(username, data_dir="/app/data"):
    """List all contacts for a user."""
    contacts_file = get_contacts_file(data_dir, username)

    if not os.path.exists(contacts_file):
        print("No contacts found.")
        return

    with open(contacts_file, "r") as f:
        contacts = json.load(f)

    print(f"\n📇 Contacts for {username}:")
    for name, info in contacts.items():
        print(f" - {name}: {info}")


def verify_contact(username, data_dir="/app/data"):
    """Verify that a given contact exists."""
    contacts_file = get_contacts_file(data_dir, username)
    if not os.path.exists(contacts_file):
        print("No contacts found.")
        return

    with open(contacts_file, "r") as f:
        contacts = json.load(f)

    contact_name = input("Enter contact name to verify: ").strip()
    if contact_name in contacts:
        print(f"✅ Contact '{contact_name}' exists.")
    else:
        print(f"❌ Contact '{contact_name}' not found.")


def admin_list(username, data_dir="/app/data"):
    """Admin function: list all user contacts (read-only)."""
    if username != "admin":
        print("Access denied.")
        return

    print("\n🗂️ Admin view: All user contact files")
    for root, dirs, files in os.walk(data_dir):
        for file in files:
            if file.endswith("_contacts.json"):
                path = os.path.join(root, file)
                print(f"\nFrom file: {path}")
                with open(path, "r") as f:
                    data = json.load(f)
                    for name, info in data.items():
                        print(f" - {name}: {info}")


def admin_clear(username, data_dir="/app/data"):
    """Admin function: clear all contact files."""
    if username != "admin":
        print("Access denied.")
        return

    for root, dirs, files in os.walk(data_dir):
        for file in files:
            if file.endswith("_contacts.json"):
                os.remove(os.path.join(root, file))
                print(f"Cleared {file}")

    print("🧹 All contact files cleared.")