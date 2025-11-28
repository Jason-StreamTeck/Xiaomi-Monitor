import sys
import asyncio
import qasync
from datetime import datetime

from PySide6.QtCore import QObject, Signal
from PySide6.QtGui import QIcon, QFont, QPalette, QColor, QMovie
from PySide6.QtCore import Qt
from PySide6.QtWidgets import (QApplication, QWidget, QTabWidget, QPushButton, QHBoxLayout, QVBoxLayout, QInputDialog,
                               QLabel, QSpinBox, QFrame, QListWidget, QTextEdit, QMessageBox, QBoxLayout, QLineEdit,
                               QComboBox, QGroupBox, QFormLayout, QFileDialog)

from core import SensorPipeline, Measurement
from services import FileLogger

class UiSignals(QObject):
    measurement = Signal(dict)
    status = Signal(str)
    devices = Signal(list)

class DeviceTab(QWidget):
    def __init__(self, pipeline: SensorPipeline, parent=None):
        super().__init__(parent)
        self.pipeline = pipeline
        self.signals = UiSignals()
        self._connecting = False
        self._connected = False
        self._data_source = None

        self.logger: FileLogger | None = None

        # Left Section
        self.scan_button = QPushButton("Scan for Devices")
        self.scan_button.setMinimumHeight(40)
        self.scan_timeout_spin = QSpinBox()
        self.scan_timeout_spin.setRange(1, 60)
        self.scan_timeout_spin.setValue(10)

        # https://icons8.com/icon/6POIOo0Oa76N/spinner icon by https://icons8.com
        self.scan_spinner = QMovie("../static/loading.gif")

        self.devices = QListWidget()
        self.devices.setFont(QFont("Courier New", weight=500))

        timeout_control = QHBoxLayout()
        timeout_control.addWidget(QLabel("Scan Duration (s)"))
        timeout_control.addWidget(self.scan_timeout_spin)

        scanner_controls = QVBoxLayout()
        scanner_controls.addLayout(timeout_control)
        scanner_controls.addWidget(self.scan_button)

        left_layout = QVBoxLayout()
        left_layout.setAlignment(Qt.AlignTop)
        left_label = QLabel("Device Scanning")
        left_layout.addWidget(left_label)
        left_layout.addWidget(self.devices)
        left_layout.addLayout(scanner_controls)

        self._update_gray_out(self.devices, self.devices.count() == 0)

        # Middle Section
        device_label = QLabel("Selected Device:")
        self.current_device = QLabel("None")

        self.interval_spin = QSpinBox()
        self.interval_spin.setRange(0, 604800)
        self.interval_spin.setValue(0)

        # https://icons8.com/icon/6POIOo0Oa76N/spinner Spinner icon by https://icons8.com
        self.connect_spinner = QMovie("../static/loading.gif")

        self.connect_button = QPushButton("Connect")
        self.connect_button.setMinimumHeight(40)
        self.connect_button.setEnabled(False)
        self.stop_button = QPushButton("Stop")
        self.stop_button.setMinimumHeight(40)
        self.stop_button.setEnabled(False)

        device_display = QHBoxLayout()
        device_display.addWidget(device_label)
        device_display.addWidget(self.current_device)

        interval_control = QHBoxLayout()
        interval_control.addWidget(QLabel("Data Capture Interval (s)"))
        interval_control.addWidget(self.interval_spin)

        connection_controls = QHBoxLayout()
        connection_controls.addWidget(self.connect_button)
        connection_controls.addWidget(self.stop_button)

        self.data_log = QTextEdit()
        self.data_log.setReadOnly(True)
        self.data_log.setFocusPolicy(Qt.FocusPolicy.NoFocus)

        self.ts_label = QLabel("Timestamp: --")
        self.temp_label = QLabel("Temperature: --")
        self.hum_label = QLabel("Humidity: --")
        self.bat_label = QLabel("Battery: --")
        self.spo2_label = QLabel("SpO2: --")
        self.pr_label = QLabel("Pulse Rate: --")

        data_font  = QFont()
        data_font.setWeight(QFont.Weight.Bold)
        self.ts_label.setFont(data_font)
        self.temp_label.setFont(data_font)
        self.hum_label.setFont(data_font)
        self.bat_label.setFont(data_font)
        self.spo2_label.setFont(data_font)
        self.pr_label.setFont(data_font)

        self.data_row_1 = QHBoxLayout()
        self.data_row_2 = QHBoxLayout()
        latest_data_layout = QVBoxLayout()
        latest_data_layout.addLayout(self.data_row_1)
        latest_data_layout.addLayout(self.data_row_2)

        self.mid_layout = QVBoxLayout()
        self.mid_layout.setAlignment(Qt.AlignTop)
        mid_label_device = QLabel("Device Connection")
        self.mid_layout.addWidget(mid_label_device)
        self.mid_layout.addLayout(device_display)
        self.mid_layout.addLayout(interval_control)
        self.mid_layout.addLayout(connection_controls)

        mid_label_data = QLabel("Live Data")
        self.mid_layout.addWidget(mid_label_data)
        self.mid_layout.addLayout(latest_data_layout)
        self.mid_layout.addWidget(self.data_log)

        self._update_gray_out(self.data_log, not bool(self.data_log.toPlainText()))

        # Right Section
        self.file_name = QLineEdit("monitor_data")
        self.file_extension = QComboBox()
        self.file_extension.addItems([".csv"])
        self.file_mode = QComboBox()
        self.file_mode.addItems(["write", "append"])
        self.file_browse_button = QPushButton("Browse...")

        self.file_group = QGroupBox("File Output")
        file_layout = QFormLayout()
        file_layout.addRow("File name: ", self.file_name)
        file_layout.addRow("Extension: ", self.file_extension)
        file_layout.addRow("Mode: ", self.file_mode)
        file_layout.addRow(self.file_browse_button)
        self.file_group.setLayout(file_layout)

        right_layout = QVBoxLayout()
        right_layout.setAlignment(Qt.AlignTop)
        right_label = QLabel("Data Transmission")
        right_layout.addWidget(right_label)
        right_layout.addWidget(self.file_group)

        # Main
        font = QFont()
        font.setPointSize(16)
        font.setBold(True)
        left_label.setFont(font)
        mid_label_device.setFont(font)
        mid_label_data.setFont(font)
        right_label.setFont(font)

        divider = QFrame()
        divider.setFrameShape(QFrame.VLine)
        divider.setFrameShadow(QFrame.Sunken)
        divider.setLineWidth(1)

        divider2 = QFrame()
        divider2.setFrameShape(QFrame.VLine)
        divider2.setFrameShadow(QFrame.Sunken)
        divider2.setLineWidth(1)

        main_layout = QHBoxLayout()
        main_layout.setSpacing(10)
        main_layout.addLayout(left_layout, 6)
        main_layout.addWidget(divider)
        main_layout.addLayout(self.mid_layout, 7)
        main_layout.addWidget(divider2)
        main_layout.addLayout(right_layout, 6)
        self.setLayout(main_layout)

        self.scan_button.clicked.connect(self.on_scan_clicked)
        self.devices.itemDoubleClicked.connect(self.on_device_selected)
        self.connect_button.clicked.connect(self.on_connect_clicked)
        self.stop_button.clicked.connect(self.on_stop_clicked)
        self.file_browse_button.clicked.connect(self.on_browse_clicked)

        self.signals.devices.connect(self.on_devices)
        self.signals.measurement.connect(self.on_measurement)


    @qasync.asyncSlot()
    async def on_scan_clicked(self):
        (style, overlay) = self._button_start_loading(self.scan_button, self.scan_spinner)
        timeout = self.scan_timeout_spin.value()
        try:
            devices = await self.pipeline.scan(timeout)
            devices_dict = [{"name": device.name or "Unknown", "address": device.address} for device in devices]
            self.signals.devices.emit(devices_dict)
        except Exception as e:
            print(f"Scan failed: {e}")
        finally:
            self._button_stop_loading(self.scan_button, self.scan_spinner, overlay, style, "Scan for Devices")


    @qasync.asyncSlot()
    async def on_connect_clicked(self):
        if self._connecting or self._connected:
            return

        self.pipeline.set_interval(self.interval_spin.value())
        self.devices.setEnabled(False)
        self.scan_button.setEnabled(False)
        self.interval_spin.setEnabled(False)
        self.file_group.setEnabled(False)
        (style, overlay) = self._button_start_loading(self.connect_button, self.connect_spinner)

        self.logger = FileLogger(self.file_name.text(), self.file_mode.currentText()[0])
        self.pipeline.register(self.logger.sub)

        self.pipeline.register(self.notify_sub)

        address = self.current_device.text().split(" (")[1].strip(")")
        try:
            await self.pipeline.connect(address)
            self._connected = True
            self._connecting = False

            self._button_stop_loading(self.connect_button, self.connect_spinner, overlay, style, "Connect")

            # https://icons8.com/icon/63262/checkmark Tick icon by https://icons8.com
            self.check_mark = QIcon("../static/tick.svg")
            self.connect_button.setIcon(self.check_mark)
            self.connect_button.setText("Connected")
            self.connect_button.setEnabled(False)
            self.stop_button.setEnabled(True)

        except Exception as e:
            QMessageBox.critical(self, "Error occurred", str(e))
            self.pipeline.hub.clear()
            self.logger.close()

            self.devices.setEnabled(True)
            self.scan_button.setEnabled(True)
            self.interval_spin.setEnabled(True)
            self.file_group.setEnabled(True)
            self._button_stop_loading(self.connect_button, self.connect_spinner, overlay, style, "Connect")


    @qasync.asyncSlot()
    async def on_stop_clicked(self):
        if not self._connected:
            return

        try:
            await self.pipeline.close()
        finally:
            self.pipeline.hub.clear()
            self.logger.close()

            self._connected = False
            self.stop_button.setEnabled(False)
            self.connect_button.setText("Connect")
            self.connect_button.setIcon(QIcon())
            self.connect_button.setEnabled(True)
            self.scan_button.setEnabled(True)
            self.file_group.setEnabled(True)
            self.devices.setEnabled(True)


    def on_browse_clicked(self):
        file_name = self.file_name.text().strip() or "monitor_data"
        extension = self.file_extension.currentText()
        output_file_name, _ = QFileDialog.getSaveFileName(
            self, "Choose file", f"{file_name}{extension}", f"{extension.upper()} Files (*{extension})"
        )

        if output_file_name:
            if output_file_name.lower().endswith(extension):
                output_file_name = output_file_name[:-len(extension)]
            self.file_name.setText(output_file_name)


    def on_devices(self, devices: dict):
        self.devices.clear()
        for device in devices:
            self.devices.addItem(f"{device['address']:17} | {device['name']}")
        self._update_gray_out(self.devices, self.devices.count() == 0)


    def on_measurement(self, data: dict):
        if not self._data_source == data["source"]:
            self._removeAllWidgets(self.data_row_1)
            self._removeAllWidgets(self.data_row_2)
            self._update_gray_out(self.data_log, False)

            if data["source"] == "XIAOMI":
                self._data_source = "XIAOMI"
                self.data_row_1.addWidget(self.ts_label)
                self.data_row_1.addWidget(self.temp_label)
                self.data_row_2.addWidget(self.hum_label)
                self.data_row_2.addWidget(self.bat_label)
            if data["source"] == "O2RING":
                self._data_source = "O2RING"
                self.data_row_1.addWidget(self.ts_label)
                self.data_row_2.addWidget(self.spo2_label)
                self.data_row_2.addWidget(self.pr_label)

        ts = datetime.fromtimestamp(data['data']['timestamp'])
        self.ts_label.setText(f"Timestamp: {ts.strftime('%d/%m %H:%M:%S')}")

        if self._data_source == "XIAOMI":
            self.temp_label.setText(f"Temperature: {data['data']['temperature']:.1f}°C")
            self.hum_label.setText(f"Humidity: {data['data']['humidity']}%")
            self.bat_label.setText(f"Battery: {data['data']['battery']}%")

        if self._data_source == "O2RING":
            self.spo2_label.setText(f"SpO2: {data['data']['spo2']}%")
            self.pr_label.setText(f"Pulse Rate: {data['data']['pr']} BPM")

        self.data_log.append(f"{str(data)}\n")


    def on_device_selected(self, device):
        info = device.text().split(" | ")
        self.current_device.setText(f"{info[1]} ({info[0]})")

        self.connect_button.setEnabled(True)
        self.connect_button.setText("Connect")
        self.stop_button.setEnabled(False)


    def _update_gray_out(self, widget: QWidget, setGray: bool):
        palette = widget.palette()
        if setGray:
            palette.setColor(QPalette.Base, QColor("#f0f0f0"))
            palette.setColor(QPalette.Text, QColor("#a0a0a0"))
        else:
            palette.setColor(QPalette.Base, QColor("white"))
            palette.setColor(QPalette.Text, QColor("black"))
        widget.setPalette(palette)


    def _button_start_loading(self, button: QPushButton, spinner: QMovie):
        button.setEnabled(False)
        button.setText("")
        button.setIcon(QIcon())
        original_style = button.styleSheet()
        button.setStyleSheet("border: none; background: transparent;")

        overlay = QLabel(button)
        overlay.setMovie(spinner)
        overlay.setAlignment(Qt.AlignCenter)
        overlay.setGeometry(button.rect())
        overlay.show()
        spinner.start()

        return original_style, overlay
    

    def _button_stop_loading(self, button: QPushButton, spinner: QMovie, overlay: QLabel, style: str, button_text: str):
        spinner.stop()
        overlay.hide()
        button.setText(button_text)
        button.setEnabled(True)
        button.setStyleSheet(style)


    def _removeAllWidgets(self, layout: QBoxLayout):
        i = 0
        while layout.count():
            item = layout.takeAt(i)
            widget = item.widget()
            if widget is not None:
                widget.deleteLater()
                i += 1


    def notify_sub(self, data: Measurement):
        if data.source == "XIAOMI":
            data_dict = {
                "source": data.source,
                "data": {
                    "timestamp": data.data.timestamp,
                    "temperature": data.data.temperature,
                    "humidity": data.data.humidity,
                    "battery": data.data.battery,
                }
            }
        if data.source == "O2RING":
            data_dict = {
                "source": data.source,
                "data": {
                    "timestamp": data.data.timestamp,
                    "spo2": data.data.spo2,
                    "pr": data.data.pr,
                }
            }
        self.signals.measurement.emit(data_dict)



class MainWindow(QWidget):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("BLE Sensor Monitoring GUI")
        self.setWindowIcon(QIcon("../static/bluetooth.svg"))
        self.setMinimumSize(960, 640)

        self.tab_widget = QTabWidget()
        self.add_tab_button = QPushButton("+")
        self.tab_widget.setMovable(True)
        self.tab_widget.setCornerWidget(self.add_tab_button)

        main_layout = QVBoxLayout()
        main_layout.addWidget(self.tab_widget)
        self.setLayout(main_layout)

        self.tabs = []
        self.new_tab()

        self.add_tab_button.clicked.connect(self.new_tab)
        self.tab_widget.tabCloseRequested.connect(self.remove_tab)
        self.tab_widget.tabBar().tabBarDoubleClicked.connect(self.rename_tab)


    def new_tab(self):
        pipeline = SensorPipeline()
        device_tab = DeviceTab(pipeline)

        index = self.tab_widget.addTab(device_tab, f"Device {len(self.tabs) + 1}")
        self.tab_widget.setCurrentIndex(index)
        self.tabs.append(device_tab)

        if len(self.tabs) > 1:
            self.tab_widget.setTabsClosable(True)
        else:
            self.tab_widget.setTabsClosable(False)


    def rename_tab(self, index):
        if index == -1: return
        current_name = self.tab_widget.tabText(index)
        new_name, ok = QInputDialog.getText(self, "Rename Tab", "New tab name:", text=current_name)
        if ok and new_name:
            self.tab_widget.setTabText(index, new_name)


    def remove_tab(self, index):
        tab = self.tab_widget.widget(index)
        try:
            asyncio.create_task(tab.pipeline.close())
        except Exception:
            pass
        self.tabs.pop(index)
        self.tab_widget.removeTab(index)

        if len(self.tabs) <= 1:
            self.tab_widget.setTabsClosable(False)



async def main():
    app = QApplication.instance()
    if app is None:
        app = QApplication(sys.argv)

    close_event = asyncio.Event()
    app.aboutToQuit.connect(close_event.set)

    window = MainWindow()
    window.show()

    await close_event.wait()

if __name__ == "__main__":
    qasync.run(main())