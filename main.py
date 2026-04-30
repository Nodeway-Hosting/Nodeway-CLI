from pydactyl import PterodactylClient
import json, sys, getpass

import pydactyl as pyd

GLOBALS_FILE = "globals.json"
PANEL_URL = "https://game.serververs.com"

def load_globals():
    try:
        with open(GLOBALS_FILE, "r") as f:
            return json.load(f)
    except FileNotFoundError:
        return {"version": "1.0.0", 
                "API_KEY": "", 
                "logged_in": False
                }
    
def save_globals(data):
    with open(GLOBALS_FILE, "w") as f:
        json.dump(data, f, indent=4)

def show_banner():
    print(r"""
 /$$   /$$                 /$$                                                    /$$$$$$  /$$       /$$$$$$
| $$$ | $$                | $$                                                   /$$__  $$| $$      |_  $$_/
| $$$$| $$  /$$$$$$   /$$$$$$$  /$$$$$$  /$$  /$$  /$$  /$$$$$$  /$$   /$$      | $$  \__/| $$        | $$  
| $$ $$ $$ /$$__  $$ /$$__  $$ /$$__  $$| $$ | $$ | $$ |____  $$| $$  | $$      | $$      | $$        | $$  
| $$  $$$$| $$  \ $$| $$  | $$| $$$$$$$$| $$ | $$ | $$  /$$$$$$$| $$  | $$      | $$      | $$        | $$  
| $$\  $$$| $$  | $$| $$  | $$| $$_____/| $$ | $$ | $$ /$$__  $$| $$  | $$      | $$    $$| $$        | $$  
| $$ \  $$|  $$$$$$/|  $$$$$$$|  $$$$$$$|  $$$$$/$$$$/|  $$$$$$$|  $$$$$$$      |  $$$$$$/| $$$$$$$$ /$$$$$$
|__/  \__/ \______/  \_______/ \_______/ \_____/\___/  \_______/ \____  $$       \______/ |________/|______/
                                                                 /$$  | $$                                  
                                                                |  $$$$$$/                                  
                                                                 \______/                                   
    """)
    print("Run 'help' to see available commands")


def cmd_help(_):
    print("""
Available commands:
help
version
login
exit
""")
    
def cmd_version(data):
    print("Version:", data.get("version", "unknown"))

def cmd_exit():
    sys.exit()

def cmd_login(data):
    apikey = getpass.getpass("Enter your client API key: ")

    try:
        client = PterodactylClient(PANEL_URL, apikey)
        account = client.client.account.get_account()
        username = account["attributes"]["username"]
        email = account["attributes"]["email"]


        data["API_KEY"] = apikey
        data["logged_in"] = True
        data["username"] = username
        data["email"] = email

        save_globals(data)

        print("Logged in successfully! With the username", username)
    except Exception as e:
        print("Login failed. Invalid API key")
        print(e)

def cmd_list_servers(data):
    apikey = data["API_KEY"]

    if not apikey:
        print("Not logged in.")
        return

    try:
        client = PterodactylClient(PANEL_URL, apikey)

        servers = client.client.servers.list_servers()

        print("Here are your servers:\n")

        for server in servers["data"]:
            attrs = server["attributes"]
            print(f"- {attrs['name']} (ID: {attrs['identifier']})")

    except Exception as e:
        print("Couldn't fetch.")
        print(e)

def cmd_srvutil(data):
    apikey = data.get("API_KEY")
    server_id = input("Enter the server ID you wanna check utilizations for: ").strip()

    if not apikey:
        print("Not logged in.")
        return
    
    try:
        client = PterodactylClient(PANEL_URL, apikey)
        util = client.client.servers.get_server_utilization(server_id)

        # Handle both response formats
        attrs = util.get("attributes", util)

        print("\nServer Utilization:")
        print(f"CPU: {attrs.get('cpu_absolute', 0)}%")
        print(f"RAM: {attrs.get('memory_bytes', 0) / 1024 / 1024:.2f} MB")
        print(f"Disk: {attrs.get('disk_bytes', 0) / 1024 / 1024:.2f} MB")
        print(f"State: {attrs.get('state', 'unknown')}")

    except Exception as e:
        print("Couldn't fetch")
        print(e)

def cmd_whoami(data):
    apikey = data.get("API_KEY")
    if not apikey:
        print("Not logged in.")
        return

    try:
        client = PterodactylClient(PANEL_URL, apikey)
        account = client.client.account.get_account()
        username = account["attributes"]["username"]
        email = account["attributes"]["email"]

        data["API_KEY"] = apikey
        data["logged_in"] = True
        data["username"] = username
        data["email"] = email

        print("WHOAMI:")
        print("username: ", username)
        print("email:", email)
        print("")
    except Exception as e:
        print("Not logged in.")
        print(e)
    



COMMANDS = {
    "help": cmd_help,
    "version": cmd_version,
    "login": cmd_login,
    "exit": cmd_exit,
    "listservers": cmd_list_servers,
    "srvutil": cmd_srvutil,
    "whoami": cmd_whoami
}

def main():
    data = load_globals()
    show_banner()

    while True:
        choice = input("> ").strip()
        command = COMMANDS.get(choice)
        if command:
            command(data)
        else:
            print("Invalid command. Try 'help'.")

if __name__ == "__main__":
    main()