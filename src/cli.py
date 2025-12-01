import os
import argparse
import asyncio
from enum import Enum, auto
from services import APIServer, SocketServer, WebSocketServer, FileLogger
from core import SensorPipeline
from dotenv import load_dotenv

load_dotenv()

class AppState(Enum):
    SCAN = auto()
    CONNECT = auto()
    QUIT = auto()

SOCKET_HOST = os.getenv("SOCKET_HOST")
SOCKET_PORT = int(os.getenv("SOCKET_PORT", '55555'))
WEBSOCKET_HOST = os.getenv("WEBSOCKET_HOST")
WEBSOCKET_PORT = int(os.getenv("WEBSOCKET_PORT", '80'))

def parse_args():
    parser = argparse.ArgumentParser(prog="Monitor", description="Xiaomi Temperature and Humidity Monitor 2", formatter_class=argparse.ArgumentDefaultsHelpFormatter)

    # BLE Options
    parser.add_argument("-t", "--scan-timeout", type=float, default=10.0, help="Duration (seconds) of each scan to find BLE devices")
    parser.add_argument("-mac", "--mac-address", type=str, help="The MAC Address of the BLE device to connect to (enables end-to-end service)")
    
    # Logging options
    parser.add_argument("-o", "--output-file", type=str, default="monitor_data", help="The name of the CSV file to output data into")
    parser.add_argument("-m", "--file-mode", type=str, choices=["w", "a"], default="w", help="Option to write or append to the output CSV file")
    parser.add_argument("-i", "--interval", type=int, help="Time interval (seconds) between data transmissions (cannot be less than device minimum)")
    parser.add_argument("-v", "--verbose", action="store_true", help="Enable visual logging of data in the terminal")
    
    # Data transmission service options
    parser.add_argument("-api", "--enable-api", action="store_true", help="Enable data transmission via API server hosting")
    parser.add_argument('--api-url', type=str, help="IP address (host) of the API server ")
    parser.add_argument("-s", "--enable-socket", action="store_true", help="Enable data transmission via sockets")
    parser.add_argument("-th", '--tcp-host', type=str, help="IP Address (host) of the socket server")
    parser.add_argument("-tp", "--tcp-port", type=int, help="Port number of the socket server")
    parser.add_argument("-ws", "--enable-websocket", action="store_true", help="Enable data transmission via web sockets")
    parser.add_argument("-wsh", "--ws-host", type=str, help="IP Address (host) of the web socket server")
    parser.add_argument("-wsp", "--ws-port", type=int, help="Port number of the web socket server")

    return parser.parse_args()

async def main(args):
    state = AppState.SCAN
    auto_connect = bool(args.mac_address)

    pipeline = SensorPipeline(args.interval, args.verbose)

    logger = FileLogger(args.output_file, args.file_mode)
    pipeline.hub.register(logger.sub)

    if args.enable_api:
        if args.api_url:
            api_server = APIServer();
            pipeline.hub.register(api_server.sub)
            await api_server.start(args.api_url)
        else:
            print("[API] Server could not initiate, url was not provided...")

    if args.enable_socket:
        host = args.tcp_host or SOCKET_HOST
        port = args.tcp_port or SOCKET_PORT
        
        if host and port:
            socket_server = SocketServer(host, port, args.verbose)
            pipeline.hub.register(socket_server.sub)
            await socket_server.start()
        else:
            print("[Socket] Server could not initiate, host and port was not provided...")

    if args.enable_websocket:
        host = args.ws_host or WEBSOCKET_HOST
        port = args.ws_port or WEBSOCKET_PORT
        
        if host and port:
            ws_server = WebSocketServer(host, port, args.verbose)
            pipeline.hub.register(ws_server.sub)
            await ws_server.start()
        else:
            print("[WS] Server could not initiate, host and port was not provided...")


    while True:
        if state == AppState.SCAN:
            if (args.mac_address):
                pipeline.address = args.mac_address
                state = AppState.CONNECT
                continue

            print("\nScanning for nearby BLE (Bluetooth Low Energy) devices...")
            devices = await pipeline.scan(args.scan_timeout)
            if not devices:
                print("No devices found. Please try moving the device closer and rescan.")
                state = AppState.SCAN
                continue

            print("Devices found:")
            for i, device in enumerate(devices, start=1):
                print(f"[{i:2}]  {device.address:17}  |  {device.name}")
                if i >= 20: break

            action = input(f"\nPlease enter your next course of action.\n1) A device number [1-{min(len(devices), 20)}]\n2) [r] to rescan\n3) [q] to quit\nInput: ").strip().lower()
            if action == "r":
                state = AppState.SCAN
            elif action == "q":
                state = AppState.QUIT
            elif action.isdigit():
                index = int(action) - 1
                if 0 <= index < min(len(devices), 20):
                    device = devices[index]
                    pipeline.address = device.address
                    print(f"Selected device: {device.name or 'Unknown'} ({device.address})")
                    state = AppState.CONNECT
                else:
                    print("Invalid device selection, please try again after rescan.")
            else:
                print("Invalid input, rescanning...")


        elif state == AppState.CONNECT:
            try:
                print(f"Attempting to connect with device...")
                await asyncio.create_task(pipeline.connect())

                print(f"Successfully established a connection with {pipeline.address}.")

                loop = asyncio.get_event_loop()
                event = asyncio.Event()
                def action_input():
                    action = input(f"Receiving data... Enter [q] to stop notification.\n")
                    if action == "q":
                        loop.call_soon_threadsafe(event.set)
                loop.run_in_executor(None, action_input)
                
                await event.wait()
                await pipeline.close()
                state = AppState.QUIT

            except Exception as e:
                print(f"Error occurred: {e}")
                if auto_connect:
                    print()
                    continue

                action = input(f"\nPlease enter your next course of action.\n1) [a] to repeatedly attempt to connect\n1) [r] to retry connecting\n2) [s] to rescan for BLE devices\n3) [q] to quit\nInput: ").strip().lower()
                if action == 'a':
                    print("Attempting connection until successful...\n")
                    auto_connect = True
                elif action == 'r':
                    print("Retrying connection...")
                    state = AppState.CONNECT
                elif action == 's':
                    print("Returning to BLE scanner...")
                    state = AppState.SCAN
                elif action == 'q':
                    state = AppState.QUIT
                else:
                    print("Invalid input, please try again.")


        elif state == AppState.QUIT:
            logger.close()
            if args.enable_api and args.api_url:
                await api_server.close()
            if args.enable_socket and (args.tcp_host or SOCKET_HOST) and (args.tcp_port or SOCKET_PORT):
                await socket_server.close()
            if args.enable_websocket and (args.ws_host or WEBSOCKET_HOST) and (args.ws_port or WEBSOCKET_PORT):
                await ws_server.close()
            print("Exiting program...")
            break


if __name__ == "__main__":
    args = parse_args()
    asyncio.run(main(args))