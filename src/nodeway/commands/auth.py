from nodeway.core.config import load_config, save_config
from nodeway.api.client import get_client
from nodeway.ui import toolkit as ui


def login(args):
    apikey = ui.password_prompt("Enter your client API key")
    if not apikey:
        ui.dim("Cancelled.")
        return

    cfg = load_config()

    with ui.Spinner("Authenticating..."):
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
        except Exception as e:
            ui.error(f"Login failed: {e}")
            return

    ui.blank()
    ui.success(f"Logged in as {ui.bold(username)}")


def logout(args):
    if not ui.confirm_prompt("This will wipe your credentials. Continue?"):
        ui.dim("Cancelled.")
        return

    cfg = load_config()
    cfg["API_KEY"] = ""
    cfg["logged_in"] = False
    cfg["username"] = ""
    cfg["email"] = ""
    save_config(cfg)
    ui.success("Credentials wiped.")


def whoami(args):
    cfg = load_config()
    if not cfg.get("logged_in"):
        ui.warn("Not logged in.")
        return

    ui.panel("Account", [
        f"{ui.C.DIM}Username:{ui.C.RESET}  {ui.C.BRIGHT_WHITE}{cfg.get('username')}{ui.C.RESET}",
        f"{ui.C.DIM}Email:{ui.C.RESET}     {ui.C.BRIGHT_WHITE}{cfg.get('email')}{ui.C.RESET}",
    ])
