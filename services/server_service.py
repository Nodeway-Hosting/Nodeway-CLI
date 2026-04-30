def list_servers(client):
    return client.client.servers.list_servers()

def get_utilization(client, server_id):
    return client.client.servers.get_server_utilization(server_id)

def send_power_action(client, server_id, action):
    return client.client.servers.send_power_action(server_id, action)

def get_websocket_details(client, server_id):
    return client.client.servers.get_websocket(server_id)
