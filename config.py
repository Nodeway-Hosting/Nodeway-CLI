import json
import os

CONFIG_DIR = os.path.expanduser("~/.nodeway")
CONFIG_FILE = os.path.join(CONFIG_DIR, "config.json")

DEFAULT_CONFIG = {
    "version": "1.0.0",
    "API_KEY": "",
    "PANEL_URL": "https://game.serververs.com",
    "logged_in": False,
    "username": "",
    "email": "",
    "default_server": ""
}

def load_config():
    if not os.path.exists(CONFIG_FILE):
        return DEFAULT_CONFIG
    
    try:
        with open(CONFIG_FILE, "r") as f:
            return {**DEFAULT_CONFIG, **json.load(f)}
    except (FileNotFoundError, json.JSONDecodeError):
        return DEFAULT_CONFIG

def save_config(data):
    if not os.path.exists(CONFIG_DIR):
        os.makedirs(CONFIG_DIR)
        
    with open(CONFIG_FILE, "w") as f:
        json.dump(data, f, indent=4)
