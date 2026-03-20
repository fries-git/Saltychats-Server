import asyncio
import json
import websockets
import random
import hashlib

URI = "ws://localhost:8080"

# make username globally accessible for send_loop
username = None

async def send_message(websocket, message):
    await websocket.send(message)

async def login_attempt(websocket):
    global username

    usernametest = input("Enter Username (or 'exit'): ")
    if usernametest.lower() in ("exit", "quit"):
        return False

    passwordtest = input("Enter Password (or 'exit'): ")
    if passwordtest.lower() in ("exit", "quit"):
        return False

    m = hashlib.md5()
    m.update(passwordtest.encode('utf-8'))
    passwordtest = m.hexdigest()

    data = {
        "command": "login",
        "data": {
            "username": usernametest,
            "password": passwordtest
        }
    }

    await send_message(websocket, json.dumps(data))

    # wait for server response
    response = await websocket.recv()
    response_data = json.loads(response)
    print(f"[SERVER] {response_data.get('message')}")

    if response_data.get("status") == "success":
        username = usernametest  # set global username
        return True
    return False

async def send_loop(websocket):
    while True:
        message = input("Enter message (or 'exit'): ")
        if message.lower() in ("exit", "quit"):
            await websocket.close()
            break
        data = {
            "command": "messageadd",
            "data": {
            "username": username,
            "message": message
            }
        }
        await websocket.send(json.dumps(data))

async def receive_loop(websocket):
    try:
        async for message in websocket:
            print(f"[RECEIVED] {message}")
    except websockets.ConnectionClosed:
        print("Connection closed by server.")

async def main():
    async with websockets.connect(URI, ping_interval=20, ping_timeout=10) as websocket:
        print("Connected to server.")

        # try login, exit if failed
        success = await login_attempt(websocket)
        if not success:
            print("Login failed. Exiting.")
            return

        # Run send + receive at the same time
        await asyncio.gather(
            send_loop(websocket),
            receive_loop(websocket)
        )

if __name__ == "__main__":
    asyncio.run(main())