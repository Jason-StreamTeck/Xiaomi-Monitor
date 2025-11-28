import csv
from core import Measurement

class FileLogger:
    def __init__(self, filename, action):
        self.filename = filename
        self.action = action
        self.file = None
        self.writer = None
        self.header: bool = None
        self.open(self.filename, self.action)

    def open(self, filename: str, action: str):
        self.file = open(filename + '.csv', action, newline="", buffering=1)
        self.writer = csv.writer(self.file)
        self.header = action != "w"

    def sub(self, data: Measurement):
        if not self.header:
            if data.source == "XIAOMI":
                self.writer.writerow(["Timestamp_s", "Temperature_C", "Humidity_%", "Battery_%"])
            if data.source == "O2RING":
                self.writer.writerow(["Timestamp_s", "SpO2_%", "PulseRate_BPM"])
            self.header = True

        self.writer.writerow([value for _key, value in data.data])
    
    def close(self):
        self.file.close()