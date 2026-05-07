from core.client import get_client
from core.utils import select_server
from services import server_service

# List all servers the user has access to
def list_servers():
    client = get_client()
    if not client:
        print("Not logged in.")
        return
    try:
        servers = server_service.list_servers(client)
        print("Your servers:\n")
        for s in servers["data"]:
            attrs = s["attributes"]
            print(f"- {attrs['name']} ({attrs['identifier']})")
    except Exception as e:
        print(f"Error: {e}")

# Show resource usage for a server
def stats(args):
    client = get_client()
    if not client:
        print("Not logged in.")
        return
    
    server_id = args[0] if args else select_server(client)
    if not server_id:
        return
    try:
        util = server_service.get_utilization(client, server_id)
        resources = util.get("resources", {})
        print("\nServer Utilization:")
        print(f"CPU: {resources.get('cpu_absolute', 0)}%")
        print(f"RAM: {resources.get('memory_bytes', 0) / 1024 / 1024:.2f} MB")
        print(f"Disk: {resources.get('disk_bytes', 0) / 1024 / 1024:.2f} MB")
        print(f"State: {util.get('current_state', 'unknown')}")
    except Exception as e:
        print(f"Error: {e}")

# Handle start, stop, restart
def power_action(action, args):
    client = get_client()
    if not client:
        print("Not logged in.")
        return
    
    server_id = args[0] if args else select_server(client)
    if not server_id:
        return
        
    try:
        server_service.send_power_action(client, server_id, action)
        print(f"Server {action} command sent.")
    except Exception as e:
        print(f"Error: {e}")

# Entry point for 'servers' command
def handle(args):
    if not args:
        print("Usage: servers <list|start|stop|restart|stats>")
        return

    cmd = args[0].lower()
    sub_args = args[1:]

    if cmd == "list":
        list_servers()
    elif cmd == "stats":
        stats(sub_args)
    elif cmd in ["start", "stop", "restart"]:
        power_action(cmd, sub_args)
    else:
        print("Invalid subcommand.")
