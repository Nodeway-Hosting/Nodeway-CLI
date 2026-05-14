import json
import threading
from core.client import get_client
from core.utils import select_server
from core import ui
from services import server_service, websocket_service
from config import load_config


def run(args):
    client = get_client()
    if not client:
        ui.warn("Not logged in.")
        return

    server_id = args[0] if args else select_server(client)
    if not server_id:
        return

    try:
        with ui.Spinner("Fetching server details..."):
            server_info = client.client.servers.get_server(server_id)
            full_uuid = server_info["uuid"]

            ws_data = server_service.get_websocket_details(client, full_uuid)
            token = ws_data["data"]["token"]
            socket_url = ws_data["data"]["socket"] + "?token=" + token
            cfg = load_config()

        def on_open(ws):
            ws.send(json.dumps({"event": "auth", "args": [token]}))

            def send_input():
                while True:
                    try:
                        cmd = input()
                        ws.send(json.dumps({"event": "send command", "args": [cmd]}))
                    except:
                        break
            threading.Thread(target=send_input, daemon=True).start()

        def on_message(ws, message):
            msg = json.loads(message)
            event = msg.get("event")
            if event == "auth success":
                ui.blank()
                ui.success("Connected to console.")
                ui.divider()
                ui.blank()
            elif event == "console output":
                output = "".join(msg["args"])
                for line in output.splitlines():
                    # Dim prefix to distinguish console output from CLI output
                    print(f"  {ui.C.DIM}│{ui.C.RESET} {line}")

        def on_error(ws, error):
            ui.error(f"WebSocket error: {error}")

        def on_close(ws, code, msg):
            ui.blank()
            ui.divider()
            ui.dim("Connection closed.")

        ui.blank()
        with ui.Spinner("Connecting to console..."):
            import time
            time.sleep(0.3)  # brief pause so spinner is visible

        websocket_service.connect_console(
            socket_url, token, cfg["PANEL_URL"],
            on_message=on_message, on_open=on_open,
            on_error=on_error, on_close=on_close
        )
    except Exception as e:
        ui.error(f"Failed to connect: {e}")
