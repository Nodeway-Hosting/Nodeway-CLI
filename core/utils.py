import sys

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

def select_server(client):
    try:
        servers = client.client.servers.list_servers()
        if not servers["data"]:
            print("No servers found.")
            return None

        print("\nSelect a server:\n")
        for i, server in enumerate(servers["data"]):
            attrs = server["attributes"]
            print(f"{i+1}. {attrs['name']} ({attrs['identifier']})")

        choice = int(input("\nEnter number: ")) - 1
        if 0 <= choice < len(servers["data"]):
            return servers["data"][choice]["attributes"]["identifier"]
        print("Invalid selection.")
        return None
    except Exception as e:
        print(f"Error selecting server: {e}")
        return None
