import os
from bleak import BleakScanner, BleakClient
import asyncio
from core import NotificationHub
from dotenv import load_dotenv

load_dotenv()

MI_DEVICE_NAME = "LYWSD03MMC"
O2_DEVICE_NAME = "O2Ring"

MI_NOTIFY_CHAR = os.getenv('MI_CHARACTERISTIC', 0)
O2_NOTIFY_CHAR = os.getenv('O2_NOTIFY_CHAR', 0)
O2_WRITE_CHAR = os.getenv('O2_WRITE_CHAR', 0)

ENABLE_REALTIME = bytes([0xAA, 0x17, 0xE8, 0x00, 0x00, 0x00, 0x00, 0x1B]) # From middleware-rust by Joe Huang

class SensorPipelineError(Exception):
    pass

class SensorPipeline:
    def __init__(self, interval: int = None):
        self.hub = NotificationHub(interval)
        self.client = None
        self.interval = interval
        # Only for O2Ring device
        self.send_task = None
        self.write_task = None

    async def scan(self, timeout: float = 10.0):
        devices = await BleakScanner.discover(timeout=timeout)
        return devices
    
    async def connect(self, address):
        if not address:
            raise SensorPipelineError("BLE device MAC Address was not provided.")
        
        async with BleakClient(address) as client:
            if not client.is_connected:
                raise RuntimeError(f"Failed to connect to {address}.")
            
            print(f"Successfully established a connection with {address}.")

            notify_char = self._get_notify_char(client)
            await client.start_notify(notify_char, self.hub.handle_notify)

            if client.name.startswith(O2_DEVICE_NAME):
                self.write_task = asyncio.create_task(self._write_to_o2ring(client))

            if self.interval:
                self.send_task = asyncio.create_task(self.hub.send_interval())

            await self._wait_for_stop()

            if self.send_task:
                self.send_task.cancel()
            if self.write_task:
                self.write_task.cancel()
            await client.stop_notify(notify_char)

    def _get_notify_char(self, client):
        if client.name == MI_DEVICE_NAME:
            return MI_NOTIFY_CHAR
        elif client.name.startswith(O2_DEVICE_NAME):
            return O2_NOTIFY_CHAR
        else:
            raise ValueError(f"Unknown BLE device type: {client.name}")
        
    async def _write_to_o2ring(self, client, interval=1):
        while True:
            await client.write_gatt_char(O2_WRITE_CHAR, ENABLE_REALTIME)
            await asyncio.sleep(interval or 1)

    async def _wait_for_stop(self):
        self._stop_event = asyncio.Event()
        await self._stop_event.wait()

    def register(self, sub):
        self.hub.register(sub)

    def close(self):
        if hasattr(self, "_stop_event"):
            self._stop_event.set()