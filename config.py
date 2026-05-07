import json
import os

# Where to store settings
CONFIG_DIR = os.path.expanduser("~/.nodeway")
CONFIG_FILE = os.path.join(CONFIG_DIR, "config.json")

# Basic settings template
DEFAULT_CONFIG = {
    "version": "1.0.0",
    "API_KEY": "",
    "PANEL_URL": "https://panel.nodeway.net",
    "logged_in": False,
    "username": "",
    "email": "",
    "default_server": ""
}

# Read config from file or use defaults
def load_config():
    if not os.path.exists(CONFIG_FILE):
        return DEFAULT_CONFIG
    
    try:
        with open(CONFIG_FILE, "r") as f:
            return {**DEFAULT_CONFIG, **json.load(f)}
    except (FileNotFoundError, json.JSONDecodeError):
        return DEFAULT_CONFIG

# Write config back to the file
def save_config(data):
    if not os.path.exists(CONFIG_DIR):
        os.makedirs(CONFIG_DIR)
        
    with open(CONFIG_FILE, "w") as f:
        json.dump(data, f, indent=4)
