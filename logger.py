import csv
from bleak.backends.characteristic import BleakGATTCharacteristic

class Logger:
    def __init__(self, filename, action, verbose):
        self.file = open(filename, action, newline="")
        self.writer = csv.writer(self.file)
        self.verbose = verbose
        if action == "w":
            self.writer.writerow(["Timestamp", "Temperature_C", "Humidity_%", "Battery_%"])
        
    def write_data(self, timestamp, temp, humid, bat):
        self.writer.writerow([timestamp, temp, humid, bat])
        if (self.verbose):
            print(f"{timestamp:18} | Temperature: {temp:3.1f}°C | Humidity: {humid:2}% | Battery: {bat:2}%")
    
    def close(self):
        self.file.close()