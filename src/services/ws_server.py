import asyncio
import json
import websockets

from models import MiMeasurement

class WebSocketServer:
    def __init__(self, host: str, port: int):
        self.host = host
        self.port = port
        self.clients = set()
        self.server = None

    async def handle_client(self, websocket: websockets.ServerConnection):
        self.clients.add(websocket)
        print(f"[WS] Client {websocket.remote_address} connected.")

        try:
            async for _ in websocket:
                pass
        except Exception as e:
            print(f"Error occured:", e)
        finally:
            self.clients.remove(websocket)
            print(f"[WS] Client {websocket.remote_address} disconnected.")

    async def start(self):
        # print(f"[WS] Starting server on {self.host}:{self.port}")
        self.server = await websockets.serve(self.handle_client, self.host, self.port)
    
    async def broadcast(self, data: MiMeasurement):
        if not self.clients:
            return
        payload = json.dumps(data.model_dump()).encode('utf-8')

        async def _safe_send(websocket, payload):
            try:
                await websocket.send(payload)
            except:
                self.clients.remove(websocket)

        await asyncio.gather(
            *[
                _safe_send(client, payload) for client in list(self.clients)
            ],
            return_exceptions=True
        )

    async def sub(self, ts: float, temp: float, humid: int, bat: int):
        measurement = MiMeasurement(
            timestamp=ts,
            temperature=temp,
            humidity=humid,
            battery=bat
        )
        await self.broadcast(measurement)

    async def close(self):
        for client in list(self.clients):
            try:
                await client.close()
            except:
                pass
        self.clients.clear()

        if self.server:
            self.server.close()
            await self.server.wait_closed()
