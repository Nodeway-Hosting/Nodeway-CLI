import sys
from config import load_config
from core import ui


def show_banner():
    """Show the startup banner with version and user info."""
    cfg = load_config()
    version = cfg.get("version", "1.0.0")
    username = cfg.get("username", "") if cfg.get("logged_in") else None
    ui.render_banner(version=version, username=username)


def select_server(client):
    """Interactive arrow-key server selector using the UI toolkit."""
    try:
        servers = client.client.servers.list_servers()
        if not servers["data"]:
            ui.warn("No servers found.")
            return None

        # Build options list
        server_data = servers["data"]

        def display_server(server, idx):
            attrs = server["attributes"]
            name = attrs["name"]
            identifier = attrs["identifier"]
            return f"{name}  {ui.C.DIM}({identifier}){ui.C.RESET}"

        selected = ui.select_menu(
            "Select a server:",
            server_data,
            display_fn=display_server
        )

        if selected is None:
            ui.dim("Cancelled.")
            return None

        return selected["attributes"]["identifier"]

    except Exception as e:
        ui.error(f"Error selecting server: {e}")
        return None
