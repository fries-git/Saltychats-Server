import asyncio
import websockets
import requests
import re
import hashlib
import sys
import datetime

global sentwelcome
sentwelcome = 0

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

print("Welcome to Saltychat! Please log in with your rotur account to continue.")

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

def input_clean(prompt=""):
    message = input(prompt)
    return message


# ANSI escape sequence stripper
ANSI_RE = re.compile(r'\x1B\[[0-?]*[ -/]*[@-~]')

def strip_ansi(s: str) -> str:
    return ANSI_RE.sub('', s)

async def send_message(websocket, messageinput):
    now = datetime.datetime.now()
    date = now.strftime("[%m/%d : %H %M %S]")
    formatteddate = textcoloring(date, GREEN)
    formattedusername = textcoloring(username, BLUE)

    if messageinput.lower() in ("exit", "quit"):
        await websocket.close()
        return
    delete_lines(1)
    await websocket.send(f"{formatteddate} {formattedusername}: {messageinput}")



async def send_loop(websocket):
    """Read blocking input in executor and send messages until exit."""
    loop = asyncio.get_event_loop()
    while True:
        messageinput = await loop.run_in_executor(None, input_clean)
        if messageinput.lower() in ("exit", "quit"):
            await websocket.close()
            break
        now = datetime.datetime.now()
        date = now.strftime("[%m/%d : %H %M %S]")
        formatteddate = textcoloring(date, GREEN)
        formattedusername = textcoloring(username, BLUE)
        delete_lines(1)
        await websocket.send(f"{formatteddate} {formattedusername}: {messageinput}")

async def receive_messages(websocket):
    try:
        async for message in websocket:
            print(message)
    except websockets.ConnectionClosed:
        print("Connection closed.")

async def main():
    global sentwelcome
    async with websockets.connect(URI) as websocket:
        if sentwelcome == 0:
            await send_message(websocket, f"{username} has joined the chat.")
            sentwelcome = 1
        print("Connected.")
        await asyncio.gather(
            receive_messages(websocket),
            send_loop(websocket),
        )

if __name__ == "__main__":
    asyncio.run(main())