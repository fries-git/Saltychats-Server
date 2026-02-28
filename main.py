import asyncio
from websockets.asyncio.server import serve
import requests
import dotenv
import os

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

    async for message in websocket:
        print(message)
        await websocket.send(message)
        if webhook == 1:
            try:
                response = requests.post(discordwebhook, json={"content": message})
                response.raise_for_status()
            except requests.exceptions.RequestException as e:
                print("Failed to send message to Discord webhook:", e)

async def main():
    ip = "localhost"
    async with serve(echo, ip, port) as server:
        print(f"Server started at {ip}:{port}")
        await server.serve_forever()


if __name__ == "__main__":
    asyncio.run(main())