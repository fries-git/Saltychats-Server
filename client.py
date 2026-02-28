import asyncio
import signal
import websockets
import requests
import re
import hashlib
import sys
import datetime
import threading
import os

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

print("Please log in with your rotur account to continue. We guarantee that your credentials are not stored or used for any other purpose than fetching your username for the chat. If you do not feel comfortable providing your credentials, you can create a new rotur account with a random email and password just for this purpose, or ping fries for help.")

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


# Line-buffer and stdin thread for package-free prompt handling
buffer = {"s": ""}
buffer_lock = threading.Lock()

def stdin_reader(loop, q, buffer, lock):
    if os.name == "nt":
        import msvcrt
        while True:
            ch = msvcrt.getwch()
            with lock:
                if ch in ("\r", "\n"):
                    line = buffer["s"]
                    buffer["s"] = ""
                    asyncio.run_coroutine_threadsafe(q.put(line), loop)
                    sys.stdout.write("\r\x1b[K> ")
                    sys.stdout.flush()
                elif ch == "\x03":
                    # Ctrl+C
                    raise KeyboardInterrupt
                elif ch == "\x08":  # backspace
                    buffer["s"] = buffer["s"][:-1]
                    sys.stdout.write("\r\x1b[K> " + buffer["s"])
                    sys.stdout.flush()
                else:
                    buffer["s"] += ch
                    sys.stdout.write(ch)
                    sys.stdout.flush()
    else:
        import tty, termios
        fd = sys.stdin.fileno()
        old = termios.tcgetattr(fd)
        tty.setcbreak(fd)
        try:
            while True:
                ch = sys.stdin.read(1)
                with lock:
                    if ch in ("\r", "\n"):
                        line = buffer["s"]
                        buffer["s"] = ""
                        asyncio.run_coroutine_threadsafe(q.put(line), loop)
                        sys.stdout.write("\r\x1b[K> ")
                        sys.stdout.flush()
                    elif ch == "\x03":
                        raise KeyboardInterrupt
                    elif ch == "\x7f":  # backspace
                        buffer["s"] = buffer["s"][:-1]
                        sys.stdout.write("\r\x1b[K> " + buffer["s"])
                        sys.stdout.flush()
                    else:
                        buffer["s"] += ch
                        sys.stdout.write(ch)
                        sys.stdout.flush()
        finally:
            termios.tcsetattr(fd, termios.TCSADRAIN, old)

async def send_message(websocket, messageinput):
    now = datetime.datetime.now()
    date = now.strftime("[%m/%d : %H %M %S]")
    formatteddate = textcoloring(date, GREEN)
    formattedusername = textcoloring(username, BLUE)

    if messageinput.lower() in ("exit", "quit"):
        await websocket.close()
        return
    await websocket.send(f"{formatteddate} {formattedusername}: {messageinput}")



async def send_loop(websocket, input_queue):
    """Read completed lines from the stdin thread via an asyncio.Queue."""
    while True:
        messageinput = await input_queue.get()
        if messageinput.lower() in ("exit", "quit"):
            await websocket.close()
            break
        await send_message(websocket, messageinput)

async def receive_messages(websocket, input_queue):
    try:
        async for message in websocket:
            with buffer_lock:
                # clear current prompt line, print the incoming message, reprint prompt + buffer
                sys.stdout.write("\r\x1b[K")
                print(message)
                sys.stdout.write("> " + buffer["s"])
                sys.stdout.flush()
    except websockets.ConnectionClosed:
        with buffer_lock:
            sys.stdout.write("\r\x1b[K")
            print("Connection closed.")
            sys.stdout.write("> " + buffer["s"])
            sys.stdout.flush()

async def main():
    global sentwelcome
    async with websockets.connect(URI) as websocket:
        if sentwelcome == 0:
            await send_message(websocket, f"{username} has joined the chat.")
            sentwelcome = 1
        print("Connected.")

        # Create input queue and start stdin reader thread
        input_queue = asyncio.Queue()
        loop = asyncio.get_event_loop()
        t = threading.Thread(target=stdin_reader, args=(loop, input_queue, buffer, buffer_lock), daemon=True)
        t.start()

        receive_task = asyncio.create_task(receive_messages(websocket, input_queue))
        send_task = asyncio.create_task(send_loop(websocket, input_queue))

        async def _shutdown():
            try:
                await send_message(websocket, f"{username} has left the chat.")
            except Exception:
                pass
            for t in (receive_task, send_task):
                t.cancel()
            try:
                await websocket.close()
            except Exception:
                pass
            print("\nDisconnected gracefully.")

        try:
                loop.add_signal_handler(signal.SIGINT, lambda: asyncio.create_task(_shutdown()))
        except NotImplementedError:
            signal.signal(signal.SIGINT, lambda s, f: asyncio.create_task(_shutdown()))

        try:
            await asyncio.gather(receive_task, send_task)
        except asyncio.CancelledError:
            pass
if __name__ == "__main__":
    asyncio.run(main())