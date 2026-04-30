import getpass
from config import load_config, save_config
from core.client import get_client

def login(args):
    apikey = getpass.getpass("Enter your client API key: ")
    cfg = load_config()
    
    try:
        from pydactyl import PterodactylClient
        client = PterodactylClient(cfg["PANEL_URL"], apikey)
        account = client.client.account.get_account()
        username = account["attributes"]["username"]
        
        cfg["API_KEY"] = apikey
        cfg["logged_in"] = True
        cfg["username"] = username
        cfg["email"] = account["attributes"]["email"]
        
        save_config(cfg)
        print(f"Logged in successfully as {username}!")
    except Exception as e:
        print(f"Login failed: {e}")

def logout(args):
    sure = input("Are you sure? (This will wipe your credentials) [y/n]: ").lower()
    if sure == "y":
        cfg = load_config()
        cfg["API_KEY"] = ""
        cfg["logged_in"] = False
        cfg["username"] = ""
        cfg["email"] = ""
        save_config(cfg)
        print("Credentials wiped.")
    else:
        print("Cancelled.")

def whoami(args):
    cfg = load_config()
    if not cfg.get("logged_in"):
        print("Not logged in.")
        return
        
    print("WHOAMI:")
    print(f"Username: {cfg.get('username')}")
    print(f"Email: {cfg.get('email')}")
