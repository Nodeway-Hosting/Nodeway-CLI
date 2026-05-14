import sys
from config import load_config
from core import utils, ui
from commands import auth, servers, console, filemanager

from prompt_toolkit import PromptSession
from prompt_toolkit.history import FileHistory
from prompt_toolkit.completion import NestedCompleter
from prompt_toolkit.formatted_text import ANSI
import os


def cmd_help(args):
    """Show available commands in a styled panel."""
    ui.panel("Commands", [
        f"{ui.C.BRIGHT_WHITE}help{ui.C.RESET}          {ui.C.DIM}—{ui.C.RESET}  Show this help message",
        f"{ui.C.BRIGHT_WHITE}version{ui.C.RESET}       {ui.C.DIM}—{ui.C.RESET}  Show version info",
        f"{ui.C.BRIGHT_WHITE}login{ui.C.RESET}         {ui.C.DIM}—{ui.C.RESET}  Log in to your account",
        f"{ui.C.BRIGHT_WHITE}logout{ui.C.RESET}        {ui.C.DIM}—{ui.C.RESET}  Log out and clear credentials",
        f"{ui.C.BRIGHT_WHITE}whoami{ui.C.RESET}        {ui.C.DIM}—{ui.C.RESET}  Show current user info",
        f"{ui.C.BRIGHT_WHITE}servers{ui.C.RESET}       {ui.C.DIM}—{ui.C.RESET}  Manage servers (list, start, stop, restart, stats)",
        f"{ui.C.BRIGHT_WHITE}console{ui.C.RESET}       {ui.C.DIM}—{ui.C.RESET}  Open server console",
        f"{ui.C.BRIGHT_WHITE}files{ui.C.RESET}         {ui.C.DIM}—{ui.C.RESET}  File manager",
        f"{ui.C.BRIGHT_WHITE}clear{ui.C.RESET}         {ui.C.DIM}—{ui.C.RESET}  Clear screen",
        f"{ui.C.BRIGHT_WHITE}exit{ui.C.RESET}          {ui.C.DIM}—{ui.C.RESET}  Exit the CLI",
    ])


def cmd_version(args):
    cfg = load_config()
    ver = cfg.get("version", "unknown")
    ui.info(f"Nodeway CLI {ui.bold(f'v{ver}')}")


def cmd_clear(args):
    ui.clear_screen()


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
    "clear": cmd_clear,
    "cls": cmd_clear,
    "exit": lambda _: sys.exit()
}


# Nested completer for tab-completion of commands + subcommands
COMPLETER = NestedCompleter.from_nested_dict({
    "help": None,
    "version": None,
    "login": None,
    "logout": None,
    "whoami": None,
    "servers": {
        "list": None,
        "start": None,
        "stop": None,
        "restart": None,
        "stats": None,
    },
    "console": None,
    "files": None,
    "fm": None,
    "clear": None,
    "cls": None,
    "exit": None,
})


def _build_prompt(cfg):
    """Build the styled prompt string showing context."""
    username = cfg.get("username", "")
    logged_in = cfg.get("logged_in", False)

    parts = f"{ui.C.DIM}nodeway{ui.C.RESET}"

    if logged_in and username:
        parts += f" {ui.C.DIM}›{ui.C.RESET} {ui.C.BRIGHT_WHITE}{username}{ui.C.RESET}"
    else:
        parts += f" {ui.C.DIM}› (not logged in){ui.C.RESET}"

    parts += f" {ui.C.BRIGHT_CYAN}›{ui.C.RESET} "
    return ANSI(parts)


def _build_toolbar(cfg):
    """Build the bottom toolbar text."""
    ver = cfg.get("version", "1.0.0")
    username = cfg.get("username", "")
    logged_in = cfg.get("logged_in", False)

    parts = [f" Nodeway CLI v{ver}"]
    if logged_in and username:
        parts.append(f"Logged in as: {username}")
    else:
        parts.append("Not logged in")
    parts.append("Ctrl+D to exit")

    return " │ ".join(parts)


def main():
    cfg = load_config()

    # Show startup banner
    utils.show_banner()

    # Set up persistent history
    history_dir = os.path.expanduser("~/.nodeway")
    if not os.path.exists(history_dir):
        os.makedirs(history_dir)
    history_file = os.path.join(history_dir, "history")

    # Create prompt session with all the goodies
    session = PromptSession(
        history=FileHistory(history_file),
        completer=COMPLETER,
        complete_while_typing=True,
    )

    while True:
        try:
            # Reload config each loop so prompt reflects login state
            cfg = load_config()

            raw = session.prompt(
                _build_prompt(cfg),
                bottom_toolbar=lambda: _build_toolbar(cfg),
            ).strip()

            if not raw:
                continue

            parts = raw.split()
            cmd = parts[0].lower()
            args = parts[1:]

            handler = COMMANDS.get(cmd)
            if handler:
                handler(args)
            else:
                ui.error(f"Unknown command: {ui.bold(cmd)}")
                ui.dim("Type 'help' to see available commands.")

        except KeyboardInterrupt:
            # Ctrl+C — don't crash, just show hint
            print()
            ui.dim("Use 'exit' or Ctrl+D to quit.")
        except EOFError:
            # Ctrl+D — clean exit
            print()
            ui.dim("Goodbye.")
            break
        except SystemExit:
            ui.dim("Goodbye.")
            break
        except Exception as e:
            ui.error(f"An error occurred: {e}")


if __name__ == "__main__":
    main()