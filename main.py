import sys
from config import load_config
from core import utils
from commands import auth, servers, console, filemanager

# Show available commands
def cmd_help(args):
    print("""
Available commands:
help        - Show this help message
version     - Show version info
login       - Log in to your account
logout      - Log out and clear credentials
whoami      - Show current user info
servers     - Manage servers (list, start, stop, restart, stats)
console     - Open server console
files       - File manager (future)
exit        - Exit the CLI
""")

# Check the current version
def cmd_version(args):
    cfg = load_config()
    print(f"Version: {cfg.get('version', 'unknown')}")

# Map commands to their handlers
COMMANDS = {
    "help": cmd_help,
    "version": cmd_version,
    "login": auth.login,
    "logout": auth.logout,
    "whoami": auth.whoami,
    "servers": servers.handle,
    "console": console.run,
    "files": filemanager.handle,
    "fm": filemanager.handle,
    "exit": lambda _: sys.exit()
}

# Main loop for the CLI
def main():
    utils.show_banner()
    while True:
        try:
            raw = input("> ").strip()
            if not raw:
                continue
            
            parts = raw.split()
            cmd = parts[0].lower()
            args = parts[1:]
            
            # Look up and run the command
            handler = COMMANDS.get(cmd)
            if handler:
                handler(args)
            else:
                print("Invalid command. Try 'help'.")
        except KeyboardInterrupt:
            print("\nExiting...")
            break
        except Exception as e:
            print(f"An error occurred: {e}")

if __name__ == "__main__":
    main()