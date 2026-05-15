import subprocess
import os
import platform
from nodeway.ui import toolkit as ui


def list_files(client, server_id, args, current_path):
    target_path = args[0] if args else current_path

    with ui.Spinner("Listing files..."):
        files = client.client.servers.files.list_files(server_id, target_path)

    ui.blank()

    if not files["data"]:
        ui.dim("Directory is empty.")
        return

    headers = ["Type", "Name", "Size"]
    rows = []
    for item in files["data"]:
        attrs = item["attributes"]
        name = attrs["name"]
        is_file = attrs["is_file"]
        size = attrs.get("size", 0)

        if is_file:
            icon = f"{ui.C.BRIGHT_BLUE}📄{ui.C.RESET}"
            size_str = _format_size(size)
        else:
            icon = f"{ui.C.BRIGHT_YELLOW}📁{ui.C.RESET}"
            size_str = f"{ui.C.DIM}—{ui.C.RESET}"

        rows.append([icon, name, size_str])

    ui.render_table(headers, rows)


def _format_size(size_bytes):
    """Format bytes into a human-readable size string."""
    if size_bytes < 1024:
        return f"{size_bytes} B"
    elif size_bytes < 1024 * 1024:
        return f"{size_bytes / 1024:.1f} KB"
    elif size_bytes < 1024 * 1024 * 1024:
        return f"{size_bytes / 1024 / 1024:.1f} MB"
    else:
        return f"{size_bytes / 1024 / 1024 / 1024:.1f} GB"


def make_directory(client, server_id, args, current_path):
    if not args:
        ui.error("Usage: mkdir <folder>")
        return

    directory_name = args[0]

    with ui.Spinner(f"Creating folder '{directory_name}'..."):
        client.client.servers.files.create_folder(server_id, directory_name, current_path)

    ui.blank()
    ui.success(f"Created folder: {ui.bold(directory_name)}")


def remove_directory(client, server_id, args, current_path):
    if not args:
        ui.error("Usage: rmdir <folder>")
        return

    target_name = args[0]
    full_path = f"{current_path}/{target_name}"

    if not ui.confirm_prompt(f"Delete folder '{target_name}'?"):
        ui.dim("Cancelled.")
        return

    with ui.Spinner(f"Removing '{target_name}'..."):
        client.client.servers.files.delete_files(server_id, [full_path])

    ui.blank()
    ui.success(f"Deleted: {ui.bold(target_name)}")


def remove_file(client, server_id, args, current_path):
    if not args:
        ui.error("Usage: rm <file>")
        return

    target_name = args[0]
    full_path = f"{current_path}/{target_name}"

    if not ui.confirm_prompt(f"Delete file '{target_name}'?"):
        ui.dim("Cancelled.")
        return

    with ui.Spinner(f"Removing '{target_name}'..."):
        client.client.servers.files.delete_files(server_id, [full_path])

    ui.blank()
    ui.success(f"Deleted: {ui.bold(target_name)}")


def concantate(client, server_id, args, current_path):
    if not args:
        ui.error("Usage: cat <file>")
        return

    file_name = args[0]
    if current_path == "/":
        full_path = f"/{file_name}"
    else:
        full_path = f"{current_path}/{file_name}"

    with ui.Spinner(f"Reading '{file_name}'..."):
        file = client.client.servers.files.get_file_contents(server_id, full_path, False)

    ui.blank()
    content_lines = file.text.splitlines()
    ui.panel(file_name, [
        f"{ui.C.DIM}{str(i+1).rjust(4)}{ui.C.RESET} {ui.C.BRIGHT_WHITE}{line}{ui.C.RESET}"
        for i, line in enumerate(content_lines)
    ])


def touch(client, server_id, args, current_path):
    if not args:
        ui.error("Usage: touch <file>")
        return

    file_name = args[0]
    if current_path == "/":
        full_path = f"/{file_name}"
    else:
        full_path = f"{current_path}/{file_name}"

    with ui.Spinner(f"Creating '{file_name}'..."):
        client.client.servers.files.write_file(server_id, full_path, None)

    ui.blank()
    ui.success(f"Created file: {ui.bold(file_name)}")


def mv_file(client, server_id, args, current_path):
    if len(args) < 2:
        ui.error("Usage: mv <source> <destination>")
        return

    source = args[0]
    destination = args[1]

    with ui.Spinner(f"Renaming '{source}' → '{destination}'..."):
        client.client.servers.files.rename_file(server_id, source, destination, current_path)

    ui.blank()
    ui.success(f"Renamed {ui.bold(source)} → {ui.bold(destination)}")


def edit_file(client, server_id, args, current_path):
    if not args:
        ui.error("Usage: edit <file>")
        return

    file_name = args[0]
    if current_path == "/":
        full_path = f"/{file_name}"
    else:
        full_path = f"{current_path}/{file_name}"

    system = platform.system()
    temp_path = f"temp_{file_name}.txt"

    with ui.Spinner(f"Downloading '{file_name}'..."):
        file_contents = client.client.servers.files.get_file_contents(server_id, full_path, False)

    ui.blank()
    ui.success("File contents downloaded.")

    with open(temp_path, "w") as f:
        f.write(file_contents.text)

    ui.info("Opening in editor...")

    if system == "Windows":
        try:
            subprocess.run(["notepad.exe", temp_path])
        except Exception as e:
            ui.error(f"Failed to open editor: {e}")
            return
    elif system == "Darwin":
        try:
            subprocess.run(["open", "-e", temp_path])
        except Exception as e:
            ui.error(f"Failed to open editor: {e}")
            return
    elif system == "Linux":
        try:
            subprocess.run(["nano", temp_path])
        except Exception as e:
            ui.error(f"Failed to open editor: {e}")
            return

    with open(temp_path, "r") as f:
        updated_contents = f.read()

    with ui.Spinner("Uploading changes..."):
        client.client.servers.files.write_file(server_id, full_path, updated_contents)

    os.remove(temp_path)
    ui.success(f"Saved changes to {ui.bold(file_name)}")