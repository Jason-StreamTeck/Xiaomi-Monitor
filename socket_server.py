import os
import socket
import threading
import json
from dotenv import load_dotenv
from typing import Tuple

load_dotenv()

def handle_client(connection: socket.socket, address: Tuple[str, int]):
    print(f"Connected to {address}")
    with connection:
        while True:
            data = connection.recv(1024)
            if not data:
                break
            try:
                decoded = json.loads(data.decode('utf-8'))
                print(f"Received from {address}: {decoded}")
            except Exception as e:
                print("Error occured:". e)

def main():
    host = os.getenv("SOCKET_HOST")
    port = int(os.getenv("SOCKET_PORT"))
    server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    server.bind((host, port))
    server.listen()
    print(f"Server listening on {host}:{port}...")

    try:
        while True:
            connection, address = server.accept()
            thread = threading.Thread(target=handle_client, args=(connection, address), daemon=True)
            thread.start()
    except Exception as e:
        print("Error occurred:", e)
    finally:
        server.close()

if __name__ == "__main__":
    main()