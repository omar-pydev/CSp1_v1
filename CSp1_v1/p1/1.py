import asyncio
import json
import os
import socket
import time
import threading
from http.server import HTTPServer, SimpleHTTPRequestHandler
import websockets

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
USER_FILE = os.path.join(BASE_DIR, "users.json")
HTTP_PORT = 8000
WS_PORT = 8765

def get_local_ip():
    try:
        with socket.socket(socket.AF_INET, socket.SOCK_DGRAM) as s:
            s.connect(("8.8.8.8", 80))
            return s.getsockname()[0]
    except Exception:
        return "127.0.0.1"


def load_users():
    try:
        with open(USER_FILE, "r", encoding="utf-8") as f:
            return json.load(f)
    except FileNotFoundError:
        return []
    except json.JSONDecodeError as exc:
        print(f"[!] Failed to read {USER_FILE}: {exc}")
        return []
    except Exception as exc:
        print(f"[!] Error loading users: {exc}")
        return []


def save_user(user):
    users = load_users()
    for u in users:
        if u.get("org") == user.get("org") and u.get("lat") == user.get("lat") and u.get("lon") == user.get("lon"):
            print("[i] Duplicate entry skipped")
            return
    users.append(user)
    with open(USER_FILE, "w", encoding="utf-8") as f:
        json.dump(users, f, indent=2)
    print(f"[+] Saved user: {user.get('org')} at {user.get('lat')},{user.get('lon')}")




async def ws_handler(ws):
    data = await ws.recv()
    user = json.loads(data)

    user["time"] = time.strftime("%Y-%m-%d %H:%M:%S")
    save_user(user)
    print(f"[+] Received WS data from {user.get('org')} at {user.get('lat')},{user.get('lon')}")


async def start_ws():
    async with websockets.serve(ws_handler, "0.0.0.0", WS_PORT):
        print(f"[+] WebSockets on ws://0.0.0.0:{WS_PORT}")
        await asyncio.Future()


def start_http():
    os.chdir(BASE_DIR)
    server = HTTPServer(("0.0.0.0", HTTP_PORT), SimpleHTTPRequestHandler)
    local_ip = get_local_ip()
    print(f"[+] HTTP SERVER : http://127.0.0.1:{HTTP_PORT}")
    print(f"[+] HTTP SERVER LAN : http://{local_ip}:{HTTP_PORT}")
    server.serve_forever()

if __name__ == "__main__":
    threading.Thread(target=start_http,daemon=True).start()
    asyncio.run(start_ws())