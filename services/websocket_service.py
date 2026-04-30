import websocket
import json
import ssl

def connect_console(socket_url, token, panel_url, on_message=None, on_open=None, on_error=None, on_close=None):
    ws = websocket.WebSocketApp(
        socket_url,
        header=[
            f"Origin: {panel_url.rstrip('/')}",
            f"Authorization: Bearer {token}"
        ],
        on_open=on_open,
        on_message=on_message,
        on_error=on_error,
        on_close=on_close
    )
    ws.run_forever(sslopt={"cert_reqs": ssl.CERT_NONE})
    return ws
