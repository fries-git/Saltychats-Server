import asyncio
from websockets.asyncio.server import serve
import requests
import dotenv
import os
import json
LOGIN_FILE = "login.json"
from http.server import SimpleHTTPRequestHandler
from socketserver import TCPServer
from functools import partial
import threading

HTTP_PORT = 8000
PUBLIC_DIR = "public"

def run_http_server():
    handler = partial(SimpleHTTPRequestHandler, directory=PUBLIC_DIR)
    with TCPServer(("0.0.0.0", HTTP_PORT), handler) as httpd:
        print(f"HTTP server started at http://localhost:{HTTP_PORT}/client.html")
        httpd.serve_forever()


def init_user_file():
    if not os.path.exists(LOGIN_FILE):
        with open(LOGIN_FILE, "w") as f:
            json.dump({}, f)  # empty dict

init_user_file()

def check_and_add_user(username, password):
    users = load_users()

    if username in users:
        return {"status": "exists", "message": "User already exists"}

    # User not found → add them
    users[username] = password
    save_users(users)

    return {"status": "created", "message": "User added"}

def load_users():
    with open(LOGIN_FILE, "r") as f:
        return json.load(f)
    
def save_users(users):
    with open(LOGIN_FILE, "w") as f:
        json.dump(users, f, indent=4)

# Track connected clients for broadcasting
connected = set()

webhook = 0
dotenv.load_dotenv()

async def handle_command(websocket, message):
    try:
        data = json.loads(message)
    except json.JSONDecodeError:
        return {"error": "Invalid JSON"}

    command = data.get("command")

    if command == "login":
        username = data.get("data", {}).get("username")
        password = data.get("data", {}).get("password")

        print(f"User_Login Call: {username}, {password}")

        users = load_users()

        if username in users:
            if users[username] == password:
                return {"status": "success", "message": "logged in"}
            else:
                return {"status": "fail", "message": "wrong password"}
        else:
            check_and_add_user(username, password)
            return {"status": "created", "message": "account doesnt exist, added"}

    elif command == "ping":
        return {"status": "success", "message": "pong"}

    elif command == "broadcast":
        msg = data.get("data", {}).get("message", "")
        return {"status": "success", "message": msg}

    else:
        return {"error": "Unknown command"}

port = os.getenv("port", 8080)
servername = os.getenv("servername", "WebSocket Server")

#This is optional. Create a .env file with the line "webhook=your_webhook_url" to use a discord webhook for logging messages.
try:
    discordwebhook=os.getenv("webhook")
except requests.exceptions.RequestException as e:
    print("Something went wrong:", e)
else:
    if discordwebhook is not None and discordwebhook != "":
        print("Discord webhook loaded successfully.")
        print("Webhook URL:", discordwebhook)
        webhook = 1

async def echo(websocket):
    # Send server name to the client when they connect
    try:
        await websocket.send(f"Welcome to {servername}! We hope you'll enjoy your stay here.")
    except Exception as e:
        print("Failed to send servername to client:", e)

    # Register client
    connected.add(websocket)
    try:
        async for message in websocket:
            print(message)
            response = await handle_command(websocket, message)

            if response:
                try:
                    await websocket.send(json.dumps(response))
                except Exception as e:
                    print("Failed to send response:", e)

            # Broadcast to all connected clients (include sender so clients see their own message)
            for ws in connected.copy():
                try:
                    if getattr(ws, "open", True):
                        await ws.send(message)
                except Exception as e:
                    print("Failed to send to a client:", e)

            # Optionally forward message to Discord webhook
            if webhook == 1:
                try:
                    response = requests.post(discordwebhook, json={"content": message})
                    response.raise_for_status()
                except requests.exceptions.RequestException as e:
                    print("Failed to send message to Discord webhook:", e)
    finally:
        # Ensure client is removed on disconnect
        try:
            connected.remove(websocket)
        except KeyError:
            pass

async def main():
    ip = "localhost"
    async with serve(echo, ip, port) as server:
        print(f"Server started at {ip}:{port}")
        await server.serve_forever()

threading.Thread(target=run_http_server, daemon=True).start()
if __name__ == "__main__":
    asyncio.run(main())