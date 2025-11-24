import websockets
import asyncio
import os
from dotenv import load_dotenv

load_dotenv()

WEBSOCKET_HOST = os.getenv("WEBSOCKET_HOST")
WEBSOCKET_PORT = int(os.getenv("WEBSOCKET_PORT", '80'))

class WebSocketClient:
    def __init__(self, host, port, callback):
        self.uri = f"ws://{host}:{port}"
        self.callback = callback
        self.websocket = None
        self.running = False

    async def listen(self):
        async with websockets.connect(self.uri) as ws:
            self.websocket = ws
            self.running = True
            print(f"[WS Client] Connected to {self.uri}.")

            try:
                async for msg in ws:
                    self.callback(msg)
            except websockets.ConnectionClosed:
                print(f"[WS Client] Connection closed.")

    def start(self):
        asyncio.create_task(self.listen())

    async def close(self):
        if self.websocket:
            await self.websocket.close()
        self.running = False

def handle_data(msg: dict):
    print("Data recieved:", msg.decode('utf-8'))

async def main():
    client = WebSocketClient(WEBSOCKET_HOST, WEBSOCKET_PORT, handle_data)
    client.start()

    try:
        await asyncio.Event().wait()
    finally:
        await client.close()

if __name__ == "__main__":
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        print("[WS Client] Closing connection...")