import sys
import time
from bleak.backends.characteristic import BleakGATTCharacteristic

class NotificationHub:
    def __init__(self):
        self.subs = []

    def register(self, sub):
        self.subs.append(sub)

    def notify(self, characteristic: BleakGATTCharacteristic, data: bytearray):
        ts = time.time()
        temp = self._decode_temp(data)
        humid = self._decode_humid(data)
        bat = self._decode_volt(data)
        for sub in self.subs:
            sub(ts, temp, humid, bat)

    # Decoding logic was obtained from the MiTemperature2 repository by JsBergbau

    def _decode_temp(self, data):
        return int.from_bytes(data[0:2], byteorder=sys.byteorder, signed=True) / 100

    def _decode_humid(self, data):
        return int.from_bytes(data[2:3], byteorder=sys.byteorder)
    
    def _decode_volt(self, data):
        voltage =  int.from_bytes(data[3:5],byteorder=sys.byteorder) / 1000
        return  min(int(round((voltage - 2.1),2) * 100), 100)