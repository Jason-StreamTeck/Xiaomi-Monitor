### Usage Instructions

1) Navigate to this directory

2) Create and activate environment
```bash
conda create -n Xiaomi-Monitor python=3.10 -y
conda activate Xiaomi-Monitor
```

3) Install dependencies
```bash
pip install -r requirements.txt
```

4) Run the service
```bash
python main.py
```

| Flag | Long Form         | Type           | Default              | Description                                                                           |
| ---- | ----------------- | -------------- | -------------------- | ------------------------------------------------------------------------------------- |
| `-d` | `--scan-duration` | `float`        | `10.0`               | Duration (in seconds) for each BLE scan.                                              |
| `-f` | `--file`          | `str`          | `"monitor_data.csv"` | Name of the CSV file for storing logged data.                                         |
| `-a` | `--address`       | `str`          | *None*               | Optional MAC address of the BLE device to connect directly (skips all services).      |
| `-v` | `--verbose`       | `bool`         | `False`              | Enable live data logging output in the terminal.                                      |
| `-m` | `--mode`          | `"w"` or `"a"` | `"w"`                | Choose whether to **write** a new file (`w`) or **append** to an existing file (`a`). |
|`-api`| `--api`           | `str`          | *None*               | Enable API data posts to a specific server.                                           |

5) Repeatedly scan until the `Mi Temperature and Humidity Monitor 2` (LYWSD03MMC) device is on the list of BLE devices and can be selected.

6) Repeatedly attempt to connect to the BLE device, ignoring the following errors (if program does not exit):
- `Could not get GATT services: Unreachable`
- `Device with address ##:##:##:##:##:## was not found.`
- A Blank Error

7) Terminate the program as you wish and check the contents of the output CSV file for data.

8) (Optional) Run the server to mock retrieve measurement data
```bash
uvicorn server:app --reload
```