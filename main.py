import os
import argparse
import asyncio
from bleak import BleakClient
from bleak import BleakScanner
from enum import Enum, auto
from logger import Logger
from api_server import APIServer
from socket_client import SocketClient
from notification_hub import NotificationHub
from dotenv import load_dotenv

load_dotenv()

class AppState(Enum):
    SCAN = auto()
    CONNECT = auto()
    QUIT = auto()

NOTIFY_CHAR = os.getenv('CHARACTERISTIC', 0)

async def scan(timeout: float):
    print("Scanning for nearby BLE (Bluetooth Low Energy) devices...")
    devices = await BleakScanner.discover(timeout=timeout)

    if not devices:
        print("No devices found. Please try moving the device closer and rescan.")
        return []

    print("Devices found:")
    for i, device in enumerate(devices, start=1):
        print(f"[{i:2}] {device.address:18} | {device.name}")
    return devices

def parse_args():
    parser = argparse.ArgumentParser(
        description="Xiaomi Temperature and Humidity Monitor 2"
    )
    parser.add_argument(
        "-t", "--scan-timeout",
        type=float,
        default=10.0,
        help="How long (seconds) for each scan of BLE devices (default = 10)"
    )
    parser.add_argument(
        "-o", "--output-file",
        type=str,
        default="monitor_data",
        help="The name of the CSV file to output data into"
    )
    parser.add_argument(
        "-mac", "--mac-address",
        type=str,
        help="The MAC Address of the BLE device to connect and enables end-to-end automatic service"
    )
    parser.add_argument(
        "-v", "--verbose",
        action="store_true",
        help="Enable visual logging of data in the terminal"
    )
    parser.add_argument(
        "-m", "--file-mode",
        type=str,
        default="w",
        help="Option to write or append to the output CSV file"
    )
    parser.add_argument(
        "-api", "--enable-api",
        action="store_true",
        help="Enable API server hosting"
    )
    parser.add_argument(
        '--api-url',
        type=str,
        help="IP address (host) of the API server "
    )
    parser.add_argument(
        "-s", "--socket",
        action="store_true",
        help="Enable data transmission via socket (host and port info can be provided via separate args or env)"
    )
    parser.add_argument(
        "-sh", '--socket-host',
        type=str,
        help="IP Address (host) of the socket server"
    )
    parser.add_argument(
        "-sp", "--socket-port",
        type=int,
        help="Port number of the socket server"
    )
    return parser.parse_args()

async def main(args):
    state = AppState.SCAN
    address = None
    auto_connect = False
    hub = NotificationHub()

    logger = Logger(args.output_file, args.file_mode, args.verbose)
    hub.register(logger.write_data)

    if args.enable_api:
        api_server = APIServer();
        hub.register(api_server.sub)
        await api_server.start(args.api_url)

    socket_client = None
    if args.socket:
        host = args.socket_host or os.getenv("SOCKET_HOST")
        port = args.socket_port or int(os.getenv("SOCKET_PORT", '55555'))
        
        if host and port:
            try:
                socket_client = SocketClient(host, port)
                socket_client.connect()
                hub.register(socket_client.send_data)
            except Exception as e:
                print(f"Error occurred:", e)
        else:
            print("Host and port information missing, Could not connect to Socket server...")

    while True:
        if state == AppState.SCAN:
            if (args.mac_address):
                address = args.address
                state = AppState.CONNECT
                continue

            devices = await scan(args.scan_timeout)

            action = input(f"\nPlease enter your next course of action.\n1) A device number [1-{len(devices)}]\n2) [r] to rescan\n3) [q] to quit\nInput: ").strip().lower()
            if action == "r":
                continue
            elif action == "q":
                state = AppState.QUIT
            elif action.isdigit():
                index = int(action) - 1
                if 0 <= index < len(devices):
                    device = devices[index]
                    address = device.address
                    print(f"Selected device: {device.name or 'Unknown'} ({device.address})")
                    state = AppState.CONNECT
                else:
                    print("Invalid device selection, please try again.")
            else:
                print("Invalid input, please try again.")


        elif state == AppState.CONNECT:
            event = asyncio.Event()
            def action_input():
                action = input(f"Receiving data from {NOTIFY_CHAR}... Enter [q] to stop notification.\n")
                if action == "q":
                    event.set()

            try:
                if not address:
                    print("A device MAC Address has not been provided...")
                    state = AppState.SCAN
                    continue
                print(f"Attempting to connect with device...")
                async with BleakClient(address) as client:
                    if client.is_connected:
                        print(f"Successfully established a connection with {address}.")
                        await client.start_notify(NOTIFY_CHAR, hub.notify)
                        asyncio.get_event_loop().run_in_executor(None, action_input)
                        await event.wait()
                        await client.stop_notify(NOTIFY_CHAR)
                        state = AppState.QUIT

            except Exception as e:
                print(f"Error occurred: {e}")
                if auto_connect or args.mac_address:
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
            if socket_client:
                socket_client.close()
            if args.enable_api:
                await api_server.close()
            print("Exiting program...")
            break

if __name__ == "__main__":
    args = parse_args()
    asyncio.run(main(args))