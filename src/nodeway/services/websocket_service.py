import websocket
import json
import ssl

def connect_console(socket_url, token, panel_url, on_message=None, on_open=None, on_error=None, on_close=None):
    try:
        ws = websocket.create_connection(
            socket_url,
            origin=panel_url.rstrip('/'),
            timeout=10,
            sslopt={"cert_reqs": ssl.CERT_NONE},
            header={
                "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36"
            }
        )
        
        if on_open:
            on_open(ws)
            
        while True:
            try:
                message = ws.recv()
                if not message:
                    break
                if on_message:
                    on_message(ws, message)
            except websocket.WebSocketConnectionClosedException:
                break
            except Exception as e:
                if on_error:
                    on_error(ws, e)
                break
                
        if on_close:
            on_close(ws, None, None)
    except Exception as e:
        if on_error:
            on_error(None, e)
        else:
            print(f"Error: {e}")
    return None
