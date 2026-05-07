from pydactyl import PterodactylClient
from config import load_config

# Helper to get a pre-configured Pterodactyl client
def get_client():
    cfg = load_config()
    if not cfg.get("API_KEY") or not cfg.get("PANEL_URL"):
        # No credentials stored
        return None
    return PterodactylClient(cfg["PANEL_URL"], cfg["API_KEY"])
