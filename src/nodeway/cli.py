import sys
import os
import typer
from typing import Optional, List
from prompt_toolkit import PromptSession
from prompt_toolkit.history import FileHistory
from prompt_toolkit.completion import NestedCompleter
from prompt_toolkit.formatted_text import ANSI

from nodeway.core.config import load_config
from nodeway.ui import toolkit as ui
from nodeway.ui import utils as ui_utils
from nodeway.commands import auth, servers, console, filemanager
from nodeway.version import __version__

app = typer.Typer(
    name="nodeway",
    help="Nodeway CLI — Manage your servers and files with ease.",
    add_completion=True,
)

# Commands

@app.command()
def login():
    """Log in to your Nodeway account."""
    auth.login([])

@app.command()
def logout():
    """Log out and clear credentials."""
    auth.logout([])

@app.command()
def whoami():
    """Show current user info."""
    auth.whoami([])

@app.command()
def version():
    """Show version info."""
    ui.info(f"Nodeway CLI {ui.bold(f'v{__version__}')}")

@app.command()
def ls():
    """List your servers."""
    servers.handle(["list"])

@app.command()
def shell(server_id: str):
    """Open server console."""
    console.run([server_id])

# REPL Logic

COMMAND_MAP = {
    "help": lambda _: app(["--help"]),
    "version": lambda _: version(),
    "login": auth.login,
    "logout": auth.logout,
    "whoami": auth.whoami,
    "servers": servers.handle,
    "console": console.run,
    "files": filemanager.handle,
    "fm": filemanager.handle,
    "clear": lambda _: ui.clear_screen(),
    "cls": lambda _: ui.clear_screen(),
    "exit": lambda _: sys.exit(),
}

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
    username = cfg.get("username", "")
    logged_in = cfg.get("logged_in", False)
    parts = [f" Nodeway CLI v{__version__}"]
    if logged_in and username:
        parts.append(f"Logged in as: {username}")
    else:
        parts.append("Not logged in")
    parts.append("Ctrl+D to exit")
    return " │ ".join(parts)

def run_repl():
    """Start the interactive REPL session."""
    cfg = load_config()
    ui_utils.show_banner()

    history_dir = os.path.expanduser("~/.nodeway")
    if not os.path.exists(history_dir):
        os.makedirs(history_dir)
    history_file = os.path.join(history_dir, "history")

    session = PromptSession(
        history=FileHistory(history_file),
        completer=COMPLETER,
        complete_while_typing=True,
    )

    while True:
        try:
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

            handler = COMMAND_MAP.get(cmd)
            if handler:
                handler(args)
            else:
                ui.error(f"Unknown command: {ui.bold(cmd)}")
                ui.dim("Type 'help' to see available commands.")

        except KeyboardInterrupt:
            print()
            ui.dim("Use 'exit' or Ctrl+D to quit.")
        except EOFError:
            print()
            ui.dim("Goodbye.")
            break
        except SystemExit:
            break
        except Exception as e:
            ui.error(f"An error occurred: {e}")

@app.callback(invoke_without_command=True)
def main(ctx: typer.Context):
    """
    Nodeway CLI entry point. 
    Runs the interactive shell if no command is provided.
    """
    if ctx.invoked_subcommand is None:
        run_repl()

if __name__ == "__main__":
    app()
