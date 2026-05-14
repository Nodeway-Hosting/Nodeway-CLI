from core.client import get_client
from core.utils import select_server
from core import ui
from services import file_service

from prompt_toolkit import PromptSession
from prompt_toolkit.history import InMemoryHistory
from prompt_toolkit.completion import WordCompleter
from prompt_toolkit.formatted_text import ANSI


# File manager command completions
FM_COMPLETER = WordCompleter([
    "ls", "cd", "mkdir", "rmdir", "rm",
    "touch", "cat", "edit", "mv",
    "clear", "cls", "help", "exit"
], ignore_case=True)


def ls_cmd(client, server_id, args, current_path):
    file_service.list_files(client, server_id, args, current_path)


def cd_cmd(client, server_id, args, current_path):
    if not args:
        return current_path

    target = args[0]

    # Go to root
    if target == "/":
        return "/"

    # Go back one directory
    if target == "..":
        if current_path == "/":
            return "/"
        parts = current_path.rstrip("/").split("/")
        parts.pop()
        if not parts or parts == [""]:
            return "/"
        return "/".join(parts)

    # Absolute path
    if target.startswith("/"):
        return target

    # Relative path
    if current_path == "/":
        return f"/{target}"
    return f"{current_path}/{target}"


def mkdir_cmd(client, server_id, args, current_path):
    file_service.make_directory(client, server_id, args, current_path)

def rmdir_cmd(client, server_id, args, current_path):
    file_service.remove_directory(client, server_id, args, current_path)

def rm_cmd(client, server_id, args, current_path):
    file_service.remove_file(client, server_id, args, current_path)

def cat_cmd(client, server_id, args, current_path):
    file_service.concantate(client, server_id, args, current_path)

def touch_cmd(client, server_id, args, current_path):
    file_service.touch(client, server_id, args, current_path)

def mv_cmd(client, server_id, args, current_path):
    file_service.mv_file(client, server_id, args, current_path)

def edit_cmd(client, server_id, args, current_path):
    file_service.edit_file(client, server_id, args, current_path)


def help_cmd(client=None, server_id=None, args=None, current_path=None):
    ui.panel("File Manager Commands", [
        f"{ui.C.BRIGHT_WHITE}ls{ui.C.RESET}                    {ui.C.DIM}—{ui.C.RESET}  List files/directories",
        f"{ui.C.BRIGHT_WHITE}cd <dir>{ui.C.RESET}              {ui.C.DIM}—{ui.C.RESET}  Change directory",
        "",
        f"{ui.C.BRIGHT_WHITE}mkdir <folder>{ui.C.RESET}        {ui.C.DIM}—{ui.C.RESET}  Create folder",
        f"{ui.C.BRIGHT_WHITE}rmdir <folder>{ui.C.RESET}        {ui.C.DIM}—{ui.C.RESET}  Remove folder",
        f"{ui.C.BRIGHT_WHITE}rm <file>{ui.C.RESET}             {ui.C.DIM}—{ui.C.RESET}  Remove file",
        "",
        f"{ui.C.BRIGHT_WHITE}touch <file>{ui.C.RESET}          {ui.C.DIM}—{ui.C.RESET}  Create empty file",
        f"{ui.C.BRIGHT_WHITE}cat <file>{ui.C.RESET}            {ui.C.DIM}—{ui.C.RESET}  View file contents",
        f"{ui.C.BRIGHT_WHITE}edit <file>{ui.C.RESET}           {ui.C.DIM}—{ui.C.RESET}  Edit file",
        "",
        f"{ui.C.BRIGHT_WHITE}mv <old> <new>{ui.C.RESET}       {ui.C.DIM}—{ui.C.RESET}  Rename file/folder",
        "",
        f"{ui.C.BRIGHT_WHITE}clear / cls{ui.C.RESET}           {ui.C.DIM}—{ui.C.RESET}  Clear terminal",
        f"{ui.C.BRIGHT_WHITE}help{ui.C.RESET}                  {ui.C.DIM}—{ui.C.RESET}  Show this help menu",
        f"{ui.C.BRIGHT_WHITE}exit{ui.C.RESET}                  {ui.C.DIM}—{ui.C.RESET}  Exit file manager",
    ])


def clear_cmd(client=None, server_id=None, args=None, current_path=None):
    ui.clear_screen()


def start_file_manager(client, server_id):
    current_path = "/"

    try:
        server = client.client.servers.get_server(server_id)
        if "attributes" in server:
            server_name = server["attributes"]["name"]
        else:
            server_name = server["name"]
    except Exception as e:
        ui.error(f"Failed to fetch server info: {e}")
        return

    COMMANDS = {
        "ls": ls_cmd,
        "cd": cd_cmd,
        "mkdir": mkdir_cmd,
        "rmdir": rmdir_cmd,
        "rm": rm_cmd,
        "cat": cat_cmd,
        "touch": touch_cmd,
        "mv": mv_cmd,
        "edit": edit_cmd,
        "help": help_cmd,
        "clear": clear_cmd,
        "cls": clear_cmd
    }

    ui.blank()
    ui.success(f"File manager opened for {ui.bold(server_name)}")
    ui.dim("Type 'help' for available commands, 'exit' to quit.")
    ui.blank()

    # Create a separate prompt session for the file manager sub-REPL
    fm_session = PromptSession(
        history=InMemoryHistory(),
        completer=FM_COMPLETER,
        complete_while_typing=False,
    )

    while True:
        try:
            prompt_text = (
                f"{ui.C.DIM}{server_name}{ui.C.RESET}"
                f"{ui.C.BRIGHT_CYAN}:{ui.C.RESET}"
                f"{ui.C.BRIGHT_WHITE}{current_path}{ui.C.RESET}"
                f" {ui.C.BRIGHT_CYAN}›{ui.C.RESET} "
            )

            command_input = fm_session.prompt(ANSI(prompt_text)).strip()

            if not command_input:
                continue

            parts = command_input.split()
            cmd = parts[0].lower()
            args = parts[1:]

            if cmd == "exit":
                ui.dim("Exiting file manager...")
                break

            elif cmd in COMMANDS:
                try:
                    result = COMMANDS[cmd](client, server_id, args, current_path)
                    if isinstance(result, str):
                        current_path = result
                except Exception as e:
                    ui.error(f"Command error: {e}")

            else:
                ui.error(f"Unknown command: {ui.bold(cmd)}")

        except KeyboardInterrupt:
            print()
            ui.dim("Use 'exit' to quit the file manager.")

        except EOFError:
            ui.dim("Exiting file manager...")
            break

        except Exception as e:
            ui.error(f"Shell error: {e}")


def handle(args):
    client = get_client()
    if not client:
        ui.warn("Not logged in.")
        return

    server_id = args[0] if args else select_server(client)
    if not server_id:
        return

    start_file_manager(client, server_id)