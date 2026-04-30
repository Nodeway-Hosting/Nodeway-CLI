from pydactyl import PterodactylClient
from config import load_config

def get_client():
    cfg = load_config()
    if not cfg.get("API_KEY") or not cfg.get("PANEL_URL"):
        return None
    return PterodactylClient(cfg["PANEL_URL"], cfg["API_KEY"])
