from core.client import get_client
from core.utils import select_server
from core import ui
from services import server_service


def list_servers():
    client = get_client()
    if not client:
        ui.warn("Not logged in.")
        return

    with ui.Spinner("Fetching servers..."):
        try:
            servers = server_service.list_servers(client)
        except Exception as e:
            ui.error(f"Failed to fetch servers: {e}")
            return

    ui.blank()

    if not servers["data"]:
        ui.dim("No servers found.")
        return

    # Build table rows
    headers = ["Name", "Identifier", "Node", "Status"]
    rows = []
    for s in servers["data"]:
        attrs = s["attributes"]
        name = attrs.get("name", "—")
        ident = attrs.get("identifier", "—")
        node = attrs.get("node", "—")

        # Color-code the status
        is_suspended = attrs.get("is_suspended", False)
        if is_suspended:
            status = f"{ui.C.BRIGHT_RED}suspended{ui.C.RESET}"
        else:
            status = f"{ui.C.BRIGHT_GREEN}active{ui.C.RESET}"

        rows.append([name, ident, str(node), status])

    ui.render_table(headers, rows)


def stats(args):
    client = get_client()
    if not client:
        ui.warn("Not logged in.")
        return

    server_id = args[0] if args else select_server(client)
    if not server_id:
        return

    with ui.Spinner("Fetching stats..."):
        try:
            util = server_service.get_utilization(client, server_id)
        except Exception as e:
            ui.error(f"Failed to fetch stats: {e}")
            return

    ui.blank()

    resources = util.get("resources", {})
    state = util.get("current_state", "unknown")

    # Color-code state
    state_colors = {
        "running": ui.C.BRIGHT_GREEN,
        "starting": ui.C.BRIGHT_YELLOW,
        "stopping": ui.C.BRIGHT_YELLOW,
        "offline": ui.C.BRIGHT_RED,
    }
    state_color = state_colors.get(state, ui.C.DIM)

    cpu = resources.get("cpu_absolute", 0)
    ram_mb = resources.get("memory_bytes", 0) / 1024 / 1024
    disk_mb = resources.get("disk_bytes", 0) / 1024 / 1024

    # Color-code CPU usage
    if cpu > 80:
        cpu_color = ui.C.BRIGHT_RED
    elif cpu > 50:
        cpu_color = ui.C.BRIGHT_YELLOW
    else:
        cpu_color = ui.C.BRIGHT_GREEN

    ui.panel(f"Stats — {server_id}", [
        f"{ui.C.DIM}State:{ui.C.RESET}   {state_color}{state}{ui.C.RESET}",
        f"{ui.C.DIM}CPU:{ui.C.RESET}     {cpu_color}{cpu}%{ui.C.RESET}",
        f"{ui.C.DIM}RAM:{ui.C.RESET}     {ui.C.BRIGHT_WHITE}{ram_mb:.2f} MB{ui.C.RESET}",
        f"{ui.C.DIM}Disk:{ui.C.RESET}    {ui.C.BRIGHT_WHITE}{disk_mb:.2f} MB{ui.C.RESET}",
    ])


def power_action(action, args):
    client = get_client()
    if not client:
        ui.warn("Not logged in.")
        return

    server_id = args[0] if args else select_server(client)
    if not server_id:
        return

    with ui.Spinner(f"Sending {action} command..."):
        try:
            server_service.send_power_action(client, server_id, action)
        except Exception as e:
            ui.error(f"Failed: {e}")
            return

    ui.blank()
    ui.success(f"Server {ui.bold(action)} command sent.")


def handle(args):
    if not args:
        ui.panel("Usage", [
            f"{ui.C.BRIGHT_WHITE}servers list{ui.C.RESET}      {ui.C.DIM}—{ui.C.RESET}  List all servers",
            f"{ui.C.BRIGHT_WHITE}servers start{ui.C.RESET}     {ui.C.DIM}—{ui.C.RESET}  Start a server",
            f"{ui.C.BRIGHT_WHITE}servers stop{ui.C.RESET}      {ui.C.DIM}—{ui.C.RESET}  Stop a server",
            f"{ui.C.BRIGHT_WHITE}servers restart{ui.C.RESET}   {ui.C.DIM}—{ui.C.RESET}  Restart a server",
            f"{ui.C.BRIGHT_WHITE}servers stats{ui.C.RESET}     {ui.C.DIM}—{ui.C.RESET}  View resource usage",
        ])
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
        ui.error(f"Unknown subcommand: {ui.bold(cmd)}")
