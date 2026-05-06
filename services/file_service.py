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