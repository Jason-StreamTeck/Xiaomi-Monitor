from fastapi import FastAPI
from models import Measurement
from urllib.parse import urlparse
import uvicorn
import asyncio

class APIServer:
    def __init__(self):
        self.app = FastAPI()
        self.latest_data: Measurement | None = None
        self.data_history: list[Measurement] = []
        
        self.app.get("/data")(self.get_latest_data)
        self.app.get("/history")(self.get_data_history)

        self.server: uvicorn.Server | None = None
        self.task: asyncio.Task | None = None
    
    def sub(self,ts: float, temp: float, humid: int, bat: int):
        measurement = Measurement(
            timestamp=ts,
            temperature=temp,
            humidity=humid,
            battery=bat
        )
        self.latest_data = measurement
        self.data_history.append(measurement)
    
    def get_latest_data(self):
        return self.latest_data
    
    def get_data_history(self):
        return self.data_history
    
    async def start(self, uri: str):
        parsed = urlparse(uri)
        host, port = parsed.hostname, parsed.port

        config = uvicorn.Config(self.app, host=host, port=port, log_config=None)
        self.server = uvicorn.Server(config)
        self.task = asyncio.create_task(self.server.serve())
        return self
    
    async def close(self):
        self.server.should_exit = True
        await self.task