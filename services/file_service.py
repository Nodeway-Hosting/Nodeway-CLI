def list_files(client, server_id, args, current_path):
    target_path = args[0] if args else current_path

    files = client.client.servers.files.list_files(
        server_id,
        target_path
    )

    print(files)