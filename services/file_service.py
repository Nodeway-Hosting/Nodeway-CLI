from colorama import Fore, Style

def list_files(client, server_id, args, current_path):
    target_path = args[0] if args else current_path

    files = client.client.servers.files.list_files(
        server_id,
        target_path
    )

    for item in files["data"]:
        attrs = item["attributes"]

        name = attrs["name"]
        is_file = attrs["is_file"]

        prefix = "[FILE]" if is_file else "[DIR]"

        print(Fore.BLUE + f"{prefix:<8} {name}" + Style.RESET_ALL)

def make_directory(client, server_id, args, current_path):
    if not args:
        print(Fore.RED + "Usage: mkdir <folder>" + Style.RESET_ALL)
        return
    target_path = current_path
    directory_name = args[0]

    directory = client.client.servers.files.create_folder(
        server_id,
        directory_name,
        target_path
    )
    print(Fore.GREEN + f"Created folder: {directory_name}" + Style.RESET_ALL)

def remove_directory(client, server_id, args, current_path):
    if not args:
        print(Fore.RED + "Usage: rmdir <folder>" + Style.RESET_ALL)
        return
    target_name = args[0]
    full_path = f"{current_path}/{target_name}"

    target = client.client.servers.files.delete_files(
        server_id,
        [full_path]
    )
    print(Fore.RED + f"Deleted target: {target_name}" + Style.RESET_ALL)

def remove_file(client, server_id, args, current_path):
    if not args:
        print(Fore.RED + "Usage: rm <folder>" + Style.RESET_ALL)
        return
    target_name = args[0]
    full_path = f"{current_path}/{target_name}"

    target = client.client.servers.files.delete_files(
        server_id,
        [full_path]
    )
    print(Fore.RED + f"Deleted target: {target_name}" + Style.RESET_ALL)

def concantate(client, server_id, args, current_path):
    if not args:
        print(Fore.RED + "Usage: cat <file>" + Style.RESET_ALL)
        return
    file_name = args[0]
    if current_path == "/":
        full_path = f"/{file_name}"
    else:
        full_path = f"{current_path}/{file_name}"

    file = client.client.servers.files.get_file_contents(
        server_id,
        full_path,
        False
    )
    print(Fore.BLUE + file.text + Style.RESET_ALL)

def touch(client, server_id, args, current_path):
    if not args:
        print(Fore.RED + "Usage: touch <file>" + Style.RESET_ALL)
        return
    file_name = args[0]
    if current_path == "/":
        full_path = f"/{file_name}"
    else:
        full_path = f"{current_path}/{file_name}"

    file = client.client.servers.files.write_file(
        server_id,
        full_path,
        None
    )
    print(Fore.GREEN + f"Created file: {file_name}" + Style.RESET_ALL)

def mv_file(client, server_id, args, current_path):
    if len(args) < 2:
        print("Usage: mv <source> <destination>")
        return

    source = args[0]
    destination = args[1]

    client.client.servers.files.rename_file(
        server_id,
        source,
        destination,
        current_path
    )

    print(Fore.GREEN + f"Renamed '{source}' -> '{destination}'" + Style.RESET_ALL)