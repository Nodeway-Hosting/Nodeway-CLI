from pydactyl import PterodactylClient
import json, sys, getpass, websocket


GLOBALS_FILE = "globals.json"
PANEL_URL = "https://game.serververs.com"

def load_globals():
    try:
        with open(GLOBALS_FILE, "r") as f:
            return json.load(f)
    except FileNotFoundError:
        return {"version": "1.0.0", "API_KEY": "", "logged_in": False}
    
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

def cmd_help(data, args):
    print("""
Available commands:
help
version
login
exit
listservers
srvutil
whoami
console
servers <start|stop|restart>
""")
    
def cmd_version(data, args):
    print("Version:", data.get("version", "unknown"))

def cmd_exit(data, args):
    sys.exit()

def cmd_login(data, args):
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

def cmd_list_servers(data, args):
    apikey = data.get("API_KEY")

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

def cmd_srvutil(data, args):
    apikey = data.get("API_KEY")

    if not apikey:
        print("Not logged in.")
        return

    server_id = input("Enter the server ID: ").strip()

    try:
        client = PterodactylClient(PANEL_URL, apikey)
        util = client.client.servers.get_server_utilization(server_id)
        attrs = util.get("attributes", util)

        print("\nServer Utilization:")
        print(f"CPU: {attrs.get('cpu_absolute', 0)}%")
        print(f"RAM: {attrs.get('memory_bytes', 0) / 1024 / 1024:.2f} MB")
        print(f"Disk: {attrs.get('disk_bytes', 0) / 1024 / 1024:.2f} MB")
        print(f"State: {attrs.get('state', 'unknown')}")

    except Exception as e:
        print("Couldn't fetch")
        print(e)

def cmd_whoami(data, args):
    apikey = data.get("API_KEY")

    if not apikey:
        print("Not logged in.")
        return

    try:
        client = PterodactylClient(PANEL_URL, apikey)
        account = client.client.account.get_account()
        username = account["attributes"]["username"]
        email = account["attributes"]["email"]

        print("WHOAMI:")
        print("username:", username)
        print("email:", email)
        print("")
    except Exception as e:
        print("Not logged in.")
        print(e)

def select_server(client):
    servers = client.client.servers.list_servers()

    if not servers["data"]:
        print("No servers found.")
        return None

    print("\nSelect a server:\n")
    for i, server in enumerate(servers["data"]):
        attrs = server["attributes"]
        print(f"{i+1}. {attrs['name']} ({attrs['identifier']})")

    try:
        choice = int(input("\nEnter number: ")) - 1
        return servers["data"][choice]["attributes"]["identifier"]
    except:
        print("Invalid selection.")
        return None

def cmd_servers(data, args):
    apikey = data.get("API_KEY")

    if not apikey:
        print("Not logged in.")
        return

    if not args:
        print("Usage: servers <start|stop|restart>")
        return

    action = args[0].lower()

    if action not in ["start", "stop", "restart"]:
        print("Invalid action.")
        return

    try:
        client = PterodactylClient(PANEL_URL, apikey)
        server_id = select_server(client)

        if not server_id:
            return

        client.client.servers.send_power_action(server_id, action)
        print(f"Server {action} command sent.")

    except Exception as e:
        print(e)

def cmd_console(data, args):
    apikey = data.get("API_KEY")

    if not apikey:
        print("Not logged in.")
        return

    try:
        client = PterodactylClient(PANEL_URL, apikey)
        server_id = select_server(client)

        if not server_id:
            return

        ws_data = client.client.servers.get_websocket(server_id)
        socket_url = ws_data["data"]["socket"]
        token = ws_data["data"]["token"]

        print("\nEstablishing connection with the console...\n")

        import threading
        import ssl

        def on_open(ws):
            ws.send(json.dumps({"event": "auth", "args": [token]}))

            def send_input():
                while True:
                    try:
                        cmd = input()
                        ws.send(json.dumps({"event": "send command", "args": [cmd]}))
                    except:
                        break

            threading.Thread(target=send_input, daemon=True).start()

        def on_message(ws, message):
            msg = json.loads(message)

            if msg.get("event") == "auth success":
                print("Connected to console.\n")
            elif msg.get("event") == "auth error":
                print("Authentication failed.")
                ws.close()
            elif msg.get("event") == "console output":
                print("".join(msg["args"]), end="")

        def on_error(ws, error):
            print("Error:", error)

        def on_close(ws, code, msg):
            print("\nConnection closed.")

        ws = websocket.WebSocketApp(
            socket_url,
            header=[
                f"Origin: {PANEL_URL.rstrip('/')}",
                f"Authorization: Bearer {token}"
            ],
            on_open=on_open,
            on_message=on_message,
            on_error=on_error,
            on_close=on_close
        )

        ws.run_forever(sslopt={"cert_reqs": ssl.CERT_NONE})

    except Exception as e:
        print("Failed to connect to console.")
        print(e)

def cmd_clean(data, args):
    apikey = data.get("API_KEY")

    if not apikey:
        print("Not logged in.")
        return

    sure = input("Are you sure? (This will wipe all your login credentials) [y/n]: ").lower()

    if sure != "y":
        print("Cancelled.")
        return

    data["API_KEY"] = ""
    data["logged_in"] = False
    data["username"] = ""
    data["email"] = ""

    save_globals(data)

    print("Credentials wiped.")


COMMANDS = {
    "help": cmd_help,
    "version": cmd_version,
    "login": cmd_login,
    "exit": cmd_exit,
    "listservers": cmd_list_servers,
    "srvutil": cmd_srvutil,
    "whoami": cmd_whoami,
    "console": cmd_console,
    "servers": cmd_servers,
    "clean": cmd_clean
}

def main():
    data = load_globals()
    show_banner()

    while True:
        raw = input("> ").strip()
        parts = raw.split()

        if not parts:
            continue

        command = parts[0]
        args = parts[1:]

        handler = COMMANDS.get(command)

        if handler:
            handler(data, args)
        else:
            print("Invalid command. Try 'help'.")

if __name__ == "__main__":
    main()