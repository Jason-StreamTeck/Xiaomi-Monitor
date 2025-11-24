import sys
import time
import asyncio
import inspect
from bleak.backends.characteristic import BleakGATTCharacteristic

class NotificationHub:
    def __init__(self, interval: int | None):
        self.subs = []
        self.interval = interval
        self.latest_data = None

    def register(self, sub):
        self.subs.append(sub)

    def handle_notify(self, characteristic: BleakGATTCharacteristic, data: bytearray):
        ts = time.time()
        temp = self._decode_temp(data)
        humid = self._decode_humid(data)
        bat = self._decode_volt(data)
        self.latest_data = (ts, temp, humid, bat)
        if self.interval == None:
            self._send_data(ts, temp, humid, bat)

    async def send_interval(self):
        while True:
            if self.latest_data:
                (_ts, temp, humid, bat) = self.latest_data
                self._send_data(time.time(), temp, humid, bat)
            await asyncio.sleep(self.interval)

    def _send_data(self, ts, temp, humid, bat):
        for sub in self.subs:
            if inspect.iscoroutinefunction(sub):
                asyncio.create_task(sub(ts, temp, humid, bat))
            else:
                sub(ts, temp, humid, bat)

    # Decoding logic was obtained from the MiTemperature2 repository by JsBergbau

    def _decode_temp(self, data: bytearray):
        return int.from_bytes(data[0:2], byteorder=sys.byteorder, signed=True) / 100

    def _decode_humid(self, data: bytearray):
        return int.from_bytes(data[2:3], byteorder=sys.byteorder)
    
    def _decode_volt(self, data: bytearray):
        voltage =  int.from_bytes(data[3:5],byteorder=sys.byteorder) / 1000
        return  min(int(round((voltage - 2.1),2) * 100), 100)