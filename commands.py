from verify import verify
import contacts 

def add():
    contacts.add_contact()

def helpu():
    print("Available Commands:")
    print("add   -> Add a new contact")
    print("list  -> List all online contacts")
    print("send  -> Transfer file to contact")
    print("verify -> Verify a contact's identity")
    print("exit  -> Exit SecureDrop")

def listc():
    contacts.list_contacts()

