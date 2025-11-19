import csv

class Logger:
    def __init__(self, filename, action, verbose):
        self.file = open(filename + '.csv', action, newline="", buffering=1)
        self.writer = csv.writer(self.file)
        self.verbose = verbose
        if action == "w":
            self.writer.writerow(["Timestamp", "Temperature_C", "Humidity_%", "Battery_%"])
        
    def write_data(self, timestamp, temp, humid, bat):
        self.writer.writerow([timestamp, temp, humid, bat])
        if (self.verbose):
            print(f"[Data] Timestamp: {timestamp:18} | Temperature: {temp:3.1f}°C | Humidity: {humid:2}% | Battery: {bat:2}%")
    
    def close(self):
        self.file.close()