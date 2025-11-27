import sys
import os
import time
import asyncio
import inspect
from bleak.backends.characteristic import BleakGATTCharacteristic
from dotenv import load_dotenv
from core import Measurement, MiData, O2Data

load_dotenv()

MI_NOTIFY_CHAR = os.getenv('MI_CHARACTERISTIC', 0)
O2_NOTIFY_CHAR = os.getenv('O2_NOTIFY_CHAR', 0)

class NotificationHub:
    def __init__(self, interval: int | None, verbose: bool):
        self.subs = []
        self.interval = interval
        self.verbose = verbose
        self.latest_data = None

    def set_interval(self, interval):
        print("INTERVAL VALUE SET")
        self.interval = interval

    def register(self, sub):
        self.subs.append(sub)

    def handle_notify(self, characteristic: BleakGATTCharacteristic, data: bytearray):
        decoded = {}
        ts = time.time()

        if characteristic.uuid == MI_NOTIFY_CHAR:
            temp = self._decode_temp(data)
            humid = self._decode_humid(data)
            bat = self._decode_volt(data)

            decoded = Measurement(
                source="XIAOMI",
                data= MiData(
                    timestamp=ts,
                    temperature=temp,
                    humidity=humid,
                    battery=bat
                )
            )

        elif characteristic.uuid == O2_NOTIFY_CHAR:
            if len(data) < 3: return
            spo2 = self._decode_spo2(data)
            pr = self._decode_pr(data)
            
            decoded = Measurement(
                source="O2RING",
                data= O2Data(
                    timestamp=ts,
                    spo2=spo2,
                    pr=pr
                )
            )

        self.latest_data = decoded
        if not self.interval:
            self._send_data(decoded)

    async def send_interval(self):
        while True:
            if self.latest_data:
                new_data = self.latest_data
                new_data.data.timestamp = time.time()
                self._send_data(new_data)
            await asyncio.sleep(self.interval)

    def _send_data(self, data: Measurement):
        if (self.verbose):
            print(f"[Data] {data}")
        for sub in self.subs:
            if inspect.iscoroutinefunction(sub):
                asyncio.create_task(sub(data))
            else:
                sub(data)

    # Decoding logic was obtained from the MiTemperature2 repository by JsBergbau

    def _decode_temp(self, data: bytearray):
        return int.from_bytes(data[0:2], byteorder=sys.byteorder, signed=True) / 100

    def _decode_humid(self, data: bytearray):
        return int.from_bytes(data[2:3], byteorder=sys.byteorder)
    
    def _decode_volt(self, data: bytearray):
        voltage =  int.from_bytes(data[3:5],byteorder=sys.byteorder) / 1000
        return  min(int(round((voltage - 2.1),2) * 100), 100)
    
    # Decoding logic was obtained from the middlware-rust repository by Joe Huang

    def _decode_spo2(self, data: bytearray):
        return data[7]

    def _decode_pr(self, data:bytearray):
        return int.from_bytes(data[8:10], byteorder=sys.byteorder)