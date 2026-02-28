import asyncio
import websockets
import requests
import hashlib
import sys
import datetime

BLACK   = "\033[30m"
RED     = "\033[31m"
GREEN   = "\033[32m"
YELLOW  = "\033[33m"
BLUE    = "\033[34m"
MAGENTA = "\033[35m"
CYAN    = "\033[36m"
WHITE   = "\033[37m"
RESET = "\033[0m"

URI = input("Enter WebSocket URI: ") or "ws://localhost:8765"

def textcoloring(text,color):
    return f"{color}{text}{RESET}"

username = input("Username: ")
password = input("Password: ")
md5_hash = hashlib.md5(password.encode()).hexdigest()

def delete_lines(n: int):
    """Delete the last n lines fully in the terminal."""
    for _ in range(n):
        # Move cursor up
        sys.stdout.write("\033[F")
        # Move to start of line
        sys.stdout.write("\r")
        # Overwrite line with spaces
        sys.stdout.write("\033[K")  # Clear to end of line
    sys.stdout.flush()

delete_lines(2)

get_user_api = "https://social.rotur.dev/get_user"

params = {
    "username": username,
    "password": md5_hash
}

try:
    response = requests.get(get_user_api, params=params)
    response.raise_for_status()  # Raises error for bad HTTP status codes

    data = response.json()

    if "error" in data and data["error"]:
        raise Exception(data["error"])

#    print("User data:", data)  # rotur account object

except Exception as err:
    print(textcoloring(f"Failed to fetch user data, please try again: {err}", RED))
    sys.exit(1)

async def send_messages(websocket):
    def input_clean(prompt=""):
        message = input(prompt)
        delete_lines(1)
        return message

    now = datetime.datetime.now()
    date = now.strftime("[%m/%d : %H %M %S]")
    formatteddate = textcoloring(date, GREEN)
    formattedusername = textcoloring(username, BLUE)

    while True:
        message = await asyncio.to_thread(input_clean, "> ")
        if message.lower() in ("exit", "quit"):
            await websocket.close()
            break
        await websocket.send(f"{formatteddate} {formattedusername}: {message}")

async def receive_messages(websocket):
    try:
        async for message in websocket:
            print(f"\n< {message}")
    except websockets.ConnectionClosed:
        print("Connection closed.")

async def main():
    async with websockets.connect(URI) as websocket:
        print("Connected.")
        await asyncio.gather(
            send_messages(websocket),
            receive_messages(websocket)
        )

if __name__ == "__main__":
    asyncio.run(main())