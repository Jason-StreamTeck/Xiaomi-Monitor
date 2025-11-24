import json
import asyncio
from models import Measurement
from typing import Set

class SocketServer:
    def __init__(self, host: str, port: int):
        self.host = host
        self.port = port
        self.clients: Set[asyncio.StreamWriter] = set()
        self.server: asyncio.Server | None = None

    async def start(self):
        self.server = await asyncio.start_server(self.handle_client, self.host, self.port)
        # print(f"[Socket] Listening on {self.host}:{self.port}...")
        return self.server
    
    async def handle_client(self, reader: asyncio.StreamReader, writer: asyncio.StreamWriter):
        address = writer.get_extra_info("peername")
        print(f"[Socket] Client {address} connected.")
        self.clients.add(writer)

        try:
            while True:
                data = await reader.read(1024)
                if not data:
                    break
        except asyncio.CancelledError:
            pass
        except (ConnectionResetError, OSError):
            print(f"[Socket] Client {address} disconnected.")
            pass
        except Exception as e:
            print(f"[Socket] Error occurred:", e)

    async def broadcast(self, data: Measurement):
        payload = json.dumps(data.model_dump()).encode('utf-8')
        for client in self.clients.copy():
            try:
                client.write(payload)
                await client.drain()
            except Exception:
                self.clients.discard(client)

    async def sub(self, ts: float, temp: float, humid: int, bat: int):
        measurement = Measurement(
            timestamp=ts,
            temperature=temp,
            humidity=humid,
            battery=bat
        )
        await self.broadcast(measurement)

    async def close(self):
        for client in self.clients:
            client.close()
            await client.wait_closed()
        self.clients.clear()

        if self.server:
            self.server.close()
            await self.server.wait_closed()