### Usage Instructions

1) Navigate to this directory

2) Create and activate environment
```bash
conda create -n Xiaomi-Monitor python=3.10 -y
conda activate Xiaomi-Monitor
```

3) Navigate to the root directory and install dependencies
```bash
pip install -r requirements.txt
```

4) Identify the `example.env` file in the repository and name it `.env` without extension.

5) Fill in the `CHARACTERISTIC` field.

- Optionally, fill `SOCKET_HOST` and `SOCKET_PORT` fields for Socket data transmission.
- Optionally, fill `WEBSOCKET_HOST` and `WEBSOCKET_PORT` fields WebSocket data transmission.

6) Run the service
```bash
cd src
python main.py

# Example usage
python main.py -t 5 -o data -v

# Example usage for API options
python main.py -api --api-url http://localhost:6123

# Example usage for Socket options
python main.py -s -sh 127.0.0.1 -sp 55555
```

| Flag   | Long Form         | Type           | Default              | Description                                                                           |
| ------ | ---------------- | -------------- | ------------------ | ------------------------------------------------------------------------------------- |
| `-t`   | `--scan-timeout`  | `float`        | `10.0`             | Duration (in seconds) for each BLE scan.                                              |
| `-mac` | `--mac-address`   | `str`          | *None*             | Optional MAC address of the BLE device to connect directly (enables end-to-end service). |
| `-o`   | `--output-file`   | `str`          | `"monitor_data"`   | Name of the CSV file for storing logged data.                                         |
| `-m`   | `--file-mode`     | `"w"` or `"a"` | `"w"`              | Choose whether to **write** a new file (`w`) or **append** to an existing file (`a`). |
| `-v`   | `--verbose`       | `bool`         | `False`            | Enable live data logging output in the terminal.                                      |
| `-api` | `--enable-api`    | `bool`         | `False`            | Enable API server for data transmission.                                              |
| *None* | `--api-url`       | `str`          | *None*             | IP address (host) of the API server.                                                 |
| `-s`   | `--enable-socket` | `bool`         | `False`            | Enable Socket server for data transmission.                                           |
| `-th`  | `--tcp-host`   | `str`          | *None*             | Host IP address of the Socket server.                                                |
| `-tp`  | `--tcp-port`   | `int`          | *None*             | Host port number of the Socket server.                                               |
| `-ws`       | `--enable-websocket` | `bool`         | `False`          | Enable WebSocket server for real-time data transmission.                                 |
| `-wsh`      | `--ws-host`          | `str`          | *None*           | Host IP address of the WebSocket server.                                                 |
| `-wsp`      | `--ws-port`          | `int`          | *None*           | Port number of the WebSocket server.                                                     |

7) Repeatedly scan until the `Mi Temperature and Humidity Monitor 2` (LYWSD03MMC) device is on the list of BLE devices and can be selected.

8) Repeatedly attempt to connect to the BLE device, ignoring the following errors (if program does not exit):
- `Could not get GATT services: Unreachable`
- `Device with address ##:##:##:##:##:## was not found.`
- A Blank Error

9) Check the contents of the output CSV file for updated data.

10) Terminate the program.

11) (Optional) Run the dummy API client to mock retrieve measurement data
```bash
python ./clients/api_client.py
```

12) (Optional) Run the dummy Socket client to mock retrieve measurement data
```bash
python ./clients/socket_client.py
```