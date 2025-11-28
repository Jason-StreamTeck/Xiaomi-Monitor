from concurrent.futures import ThreadPoolExecutor
from fastapi import FastAPI
from core import Measurement
from urllib.parse import urlparse
import uvicorn
import asyncio

class APIServer:
    def __init__(self, uri = None):
        self.app = FastAPI()
        self.uri = uri
        self.latest_data: Measurement | None = None
        self.data_history: list[Measurement] = []
        self.executor = ThreadPoolExecutor(1)
        
        self.app.get("/data")(self.get_latest_data)
        self.app.get("/history")(self.get_data_history)

        self.server: uvicorn.Server | None = None
        self.task: asyncio.Task | None = None
    
    def sub(self, data: Measurement):
        self.latest_data = data
        self.data_history.append(data)
    
    def get_latest_data(self):
        return self.latest_data
    
    def get_data_history(self):
        return self.data_history
    
    async def start(self, uri: str = None):
        if uri: self.uri = uri
        parsed = urlparse(self.uri)
        host, port = parsed.hostname, parsed.port

        config = uvicorn.Config(self.app, host=host, port=port, log_config=None, loop="asyncio", lifespan="off", interface="asgi3")
        self.server = uvicorn.Server(config)

        loop = asyncio.get_running_loop()
        self.task = loop.run_in_executor(self.executor, self.server.run)
        return self
    
    async def close(self):
        if self.server:
            self.server.should_exit = True
        if self.task:
            await self.task
        self.executor.shutdown(wait=False)