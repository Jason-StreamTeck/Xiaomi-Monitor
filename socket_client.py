import socket
import threading
import queue
import json

class SocketClient:
    def __init__(self, host, port):
        self.host = host
        self.port = port
        self.sock = None
        self.msgs = queue.Queue()
        self.running = False

    def connect(self):
        self.sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.sock.connect((self.host, self.port))
        self.running = True
        threading.Thread(target=self._comms, daemon=True).start()

    def _comms(self):
        while self.running:
            try:
                msg = self.msgs.get(timeout=1)
                self.sock.sendall(msg.encode('utf-8'))
            except queue.Empty:
                continue
            except Exception as e:
                print(f"Error occurred:", e)
    
    def send_data(self, timestamp, temp, humid, bat):
        self.msgs.put(json.dumps({
            "timestamp": timestamp,
            "temperature": temp,
            "humidity": humid,
            "battery": bat
        }))

    def close(self):
        self.running = False
        if self.sock:
            self.sock.close()