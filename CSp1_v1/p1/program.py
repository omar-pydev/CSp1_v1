import requests
import json
import asyncio
import websockets
from tkinter import *

SERVER_WS = "ws://127.0.0.1:8765"  # local server websocket address for same-machine testing


def get_ip_info():
    r = requests.get("https://ipinfo.io/json", timeout=5)
    return r.json()


def is_allowed(info):
    return True


async def send(datainfo):
    async with websockets.connect(SERVER_WS) as ws:
        await ws.send(json.dumps(datainfo))


def pro1():
    root = Tk()
    root.geometry("100x100")
    root.title("omar")
    Label(root, text="iraq", font=("Arial", 12)).pack(expand=True)
    root.mainloop()


def pro2(message="error"):
    root = Tk()
    root.geometry("250x150")
    root.title("omar")
    Label(root, text="iraq", font=("Arial", 12)).pack(pady=10)
    Label(root, text=message, font=("Arial", 10), fg="red").pack()
    root.mainloop()


def main():
    info = get_ip_info()

    # allow any country for local network testing
    if not is_allowed(info):
        pro2()
        return  # stop

    try:
        lat, lon = map(float, info["loc"].split(","))
    except Exception as exc:
        message = f"Failed to read location: {exc}"
        print(f"[!] {message}")
        pro2(message)
        return

    datainfo = {
        "country": info.get("country"),
        "city": info.get("city"),
        "org": info.get("org"),
        "lat": lat,
        "lon": lon,
    }

    try:
        asyncio.run(send(datainfo))
    except Exception as exc:
        message = f"WebSocket send failed: {exc}"
        print(f"[!] {message}")
        pro2(message)
        return

    pro1()


if __name__ == "__main__":
    main()
