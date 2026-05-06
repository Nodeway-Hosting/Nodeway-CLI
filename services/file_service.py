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

        print(f"{prefix:<8} {name}")

    