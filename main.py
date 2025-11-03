import argparse
import asyncio
from bleak import BleakClient
from bleak import BleakScanner
from enum import Enum, auto
from logger import Logger
from api import API
from notification_hub import NotificationHub

class AppState(Enum):
    SCAN = auto()
    CONNECT = auto()
    QUIT = auto()

TEMP_HUMID_NOTIFY_READ = 'ebe0ccc1-7a0a-4b0c-8a1a-6ff2997da3a6'

async def scan(duration: float):
    print("Scanning for nearby BLE (Bluetooth Low Energy) devices...")
    devices = await BleakScanner.discover(timeout=duration)

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
        "-d", "--scan-duration",
        type=float,
        default=10.0,
        help="How long (seconds) for each scan of BLE devices (default = 10)"
    )
    parser.add_argument(
        "-f", "--file",
        type=str,
        default="monitor_data.csv",
        help="The name of the CSV file to output data into"
    )
    parser.add_argument(
        "-a", "--address",
        type=str,
        help="The MAC Address of the BLE device to connect and enables end-to-end automatic service"
    )
    parser.add_argument(
        "-v", "--verbose",
        action="store_true",
        help="Enable visual logging of data in the terminal"
    )
    parser.add_argument(
        "-m", "--mode",
        type=str,
        default="w",
        help="Option to write or append to the output CSV file"
    )
    parser.add_argument(
        "-api", "--api",
        type=str,
        help="Enable API data posting and the site address of the API server "
    )
    return parser.parse_args()

async def main(args):
    state = AppState.SCAN
    address = None
    hub = NotificationHub()
    logger = Logger(args.file, args.mode, args.verbose)
    hub.register(logger.write_data)
    if args.api:
        api = API(args.api)
        hub.register(api.post_data)
    auto_connect = False

    while True:
        if state == AppState.SCAN:
            if (args.address):
                address = args.address
                state = AppState.CONNECT
                continue

            devices = await scan(args.scan_duration)

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
                action = input(f"Receiving data from {TEMP_HUMID_NOTIFY_READ}... Enter [q] to stop notification.\n")
                if action == "q":
                    event.set()

            try:
                print(f"Attempting to connect with device...")
                async with BleakClient(address) as client:
                    if client.is_connected:
                        print(f"Successfully established a connection with {address}.")
                        await client.start_notify(TEMP_HUMID_NOTIFY_READ, hub.notify)
                        asyncio.get_event_loop().run_in_executor(None, action_input)
                        await event.wait()
                        await client.stop_notify(TEMP_HUMID_NOTIFY_READ)
                        state = AppState.QUIT

            except Exception as e:
                print(f"Error occurred: {e}")
                if auto_connect or args.address:
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
            print("Exiting program...")
            logger.close()
            break

if __name__ == "__main__":
    args = parse_args()
    asyncio.run(main(args))