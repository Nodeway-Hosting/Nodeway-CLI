from core.client import get_client
from core.utils import select_server
from services import server_service, file_service

def ls_cmd(client, server_id, args, current_path):
    client = get_client()
    if not client:
        print("Not logged in.")
        return
    try:
        file_service.list_files(
            client,
            server_id,
            args,
            current_path
        )
    except Exception as e:
        print(f"Error: {e}")

def cd_cmd(client, server_id, args, current_path):
    # No target provided
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
        "cd": cd_cmd
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

            elif cmd == "pwd":
                print(current_path)

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
        print("Not logged in.")
        return

    server_id = args[0] if args else select_server(client)

    if not server_id:
        return

    start_file_manager(client, server_id)