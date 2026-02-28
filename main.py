import asyncio
from websockets.asyncio.server import serve
import requests
import dotenv
import os

# Track connected clients for broadcasting
connected = set()

webhook = 0
dotenv.load_dotenv()

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


if __name__ == "__main__":
    asyncio.run(main())