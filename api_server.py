from fastapi import FastAPI
from models import Measurement
from urllib.parse import urlparse
from typing import Tuple
import uvicorn
import asyncio

app = FastAPI()

latest_data: Measurement | None = None
data_history: list[Measurement] = []

def api_sub(ts, temp, humid, bat):
    global latest_data
    measurement = Measurement(
        timestamp=ts,
        temperature=temp,
        humidity=humid,
        battery=bat
    )
    latest_data = measurement
    data_history.append(measurement)

async def handle_api_server(uri: str) -> Tuple[asyncio.Task, asyncio.Event, uvicorn.Server]:
    parsed = urlparse(uri)
    host, port = parsed.hostname, parsed.port

    shutdown_event = asyncio.Event()
    config = uvicorn.Config(app, host=host, port=port, log_config=None)
    server = uvicorn.Server(config)
    server_task = asyncio.create_task(server.serve())

    return server_task, shutdown_event, server

async def shutdown_api_server(server_task: asyncio.Task, server: uvicorn.Server):
    server.should_exit = True
    await server_task

@app.get("/data")
def get_latest_data():
    return latest_data

@app.get("/history")
def get_history():
    return data_history