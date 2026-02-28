import asyncio
from websockets.asyncio.server import serve


async def echo(websocket):
    async for message in websocket:
        await websocket.send(message)
        print(message)


async def main():
    port = 5613
    ip = "localhost"
    async with serve(echo, ip, port) as server:
        print(f"Server started at {ip}:{port}")
        await server.serve_forever()


if __name__ == "__main__":
    asyncio.run(main())