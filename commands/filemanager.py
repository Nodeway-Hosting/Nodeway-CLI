from core.client import get_client
from core.utils import select_server
from services import file_service
from colorama import Fore, Style
import os
import platform

def ls_cmd(client, server_id, args, current_path):
    file_service.list_files(
        client,
        server_id,
        args,
        current_path
    )


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

    # Absolute path thingy
    if target.startswith("/"):
        return target

    # Relative path thingy
    if current_path == "/":
        return f"/{target}"

    return f"{current_path}/{target}"


def mkdir_cmd(client, server_id, args, current_path):
    file_service.make_directory(
        client,
        server_id,
        args,
        current_path
    )

def rmdir_cmd(client, server_id, args, current_path):
    file_service.remove_directory(
        client,
        server_id,
        args,
        current_path
    )

def rm_cmd(client, server_id, args, current_path):
    file_service.remove_file(
        client,
        server_id,
        args,
        current_path
    )

def cat_cmd(client, server_id, args, current_path):
    file_service.concantate(
        client,
        server_id,
        args,
        current_path
    )

def touch_cmd(client, server_id, args, current_path):
    file_service.touch(
        client,
        server_id,
        args,
        current_path
    )

def mv_cmd(client, server_id, args, current_path):
    file_service.mv_file(
        client,
        server_id,
        args,
        current_path
    )

def edit_cmd(client, server_id, args, current_path):
    file_service.edit_file(
        client,
        server_id,
        args,
        current_path
    )

def help_cmd(client=None, server_id=None, args=None, current_path=None):
    print(Fore.CYAN + """
Available Commands:

ls                     List files/directories
cd <dir>               Change directory

mkdir <folder>         Create folder
rmdir <folder>         Remove folder
rm <file>              Remove file

touch <file>           Create empty file
cat <file>             View file contents
edit <file>            Edit file

mv <old> <new>         Rename file/folder

clear / cls            Clear terminal
help                   Show this help menu
exit                   Exit file manager
""" + Style.RESET_ALL)
    
def clear_cmd(client=None, server_id=None, args=None, current_path=None):
    system = platform.system()

    if system == "Windows":
        os.system("cls")
    else:
        os.system("clear")


def start_file_manager(client, server_id):
    current_path = "/"
    running = True

    try:
        server = client.client.servers.get_server(server_id)

        if "attributes" in server:
            server_name = server["attributes"]["name"]
        else:
            server_name = server["name"]

    except Exception as e:
        print(f"Failed to fetch server info: {e}")
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

    while running:
        try:
            command_input = input(f"{server_name}:{current_path}> ").strip()

            if not command_input:
                continue

            parts = command_input.split()

            cmd = parts[0].lower()
            args = parts[1:]

            if cmd == "exit":
                print("Exiting file manager...")
                break

            elif cmd in COMMANDS:
                try:
                    result = COMMANDS[cmd](
                        client,
                        server_id,
                        args,
                        current_path
                    )

                    if isinstance(result, str):
                        current_path = result

                except Exception as e:
                    print(f"Command error: {e}")

            else:
                print(f"Unknown command: {cmd}")

        except KeyboardInterrupt:
            print("\nUse 'exit' to quit.")

        except Exception as e:
            print(f"Shell error: {e}")
            

            
def handle(args):
    client = get_client()

    if not client:
        print(Fore.RED + "Not logged in." + Style.RESET_ALL)
        return

    server_id = args[0] if args else select_server(client)

    if not server_id:
        return

    start_file_manager(client, server_id)