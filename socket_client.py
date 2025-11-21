import socket
import threading
import json
import os
import asyncio
from dotenv import load_dotenv

load_dotenv()

SOCKET_HOST = os.getenv("SOCKET_HOST")
SOCKET_PORT = int(os.getenv("SOCKET_PORT", '55555'))

class SocketClient:
    def __init__(self, host, port, callback):
        self.host = host
        self.port = port
        self.sock = None
        self.callback = callback
        self.running = False

    def connect(self):
        self.sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.sock.connect((self.host, self.port))
        self.running = True
        print(f"Client connected to {self.host}:{self.port}")
        threading.Thread(target=self._recv_loop, daemon=True).start()

    def _recv_loop(self):
        while self.running:
            try:
                data = self.sock.recv(1024)
                if not data:
                    break
                decoded = json.loads(data.decode('utf-8'))
                self.callback(decoded)
            except Exception as e:
                print(f"Error occurred:", e)
    
    def close(self):
        self.running = False
        if self.sock:
            self.sock.close()

def handle_data(msg: dict):
    print("Data recieved:", msg)

async def main():
    client = SocketClient(SOCKET_HOST, SOCKET_PORT, handle_data)
    client.connect()

    try:
        while True:
            # keep the main thread alive
            await asyncio.sleep(1)
    except KeyboardInterrupt:
        client.close()

asyncio.run(main())