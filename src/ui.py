import sys
import asyncio
import qasync

from PySide6.QtCore import QObject, Signal
from PySide6.QtGui import QIcon, QFont, QPalette, QColor, QMovie
from PySide6.QtCore import Qt
from PySide6.QtWidgets import (QApplication, QWidget, QTabWidget, QPushButton, QHBoxLayout, QVBoxLayout, QInputDialog, QLabel, QSpinBox, QFrame, QListWidget)

from core import SensorPipeline
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

        # Left Section
        self.scan_button = QPushButton("Scan for Devices")
        self.scan_button.setMinimumHeight(40)
        self.scan_timeout_spin = QSpinBox()
        self.scan_timeout_spin.setRange(1, 60)
        self.scan_timeout_spin.setValue(10)

        # https://icons8.com/icon/6POIOo0Oa76N/spinner icon by https://icons8.com
        self.spinner = QMovie("../static/loading.gif")

        self.devices = QListWidget()
        self.devices.setFont(QFont("Courier New", weight=500))

        timeout_control = QHBoxLayout()
        timeout_control.addWidget(QLabel("Timeout Duration (s)"))
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

        self.update_gray_out()

        # Middle Section
        device_label = QLabel("Selected Device:")
        self.current_device = QLabel("None")
        self.connect_button = QPushButton("Connect")
        self.connect_button.setMinimumHeight(40)
        self.stop_button = QPushButton("Stop")
        self.stop_button.setMinimumHeight(40)

        device_display = QHBoxLayout()
        device_display.addWidget(device_label)
        device_display.addWidget(self.current_device)

        connection_controls = QHBoxLayout()
        connection_controls.addWidget(self.connect_button)
        connection_controls.addWidget(self.stop_button)

        mid_layout = QVBoxLayout()
        mid_layout.setAlignment(Qt.AlignTop)
        mid_label = QLabel("Device Connection")
        mid_layout.addWidget(mid_label)
        mid_layout.addLayout(device_display)
        mid_layout.addLayout(connection_controls)

        # Right Section
        right_layout = QVBoxLayout()
        right_layout.setAlignment(Qt.AlignTop)
        right_label = QLabel("Data Capture")
        right_layout.addWidget(right_label)

        # Main
        font = QFont()
        font.setPointSize(16)
        font.setBold(True)
        left_label.setFont(font)
        mid_label.setFont(font)
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
        main_layout.addLayout(left_layout, 1)
        main_layout.addWidget(divider)
        main_layout.addLayout(mid_layout, 1)
        main_layout.addWidget(divider2)
        main_layout.addLayout(right_layout, 1)
        self.setLayout(main_layout)

        self.scan_button.clicked.connect(self.on_scan_clicked)

        self.signals.devices.connect(self.on_devices)

    @qasync.asyncSlot()
    async def on_scan_clicked(self):
        self.scan_button.setEnabled(False)
        self.scan_button.setText("")
        self.scan_button.setIcon(QIcon())
        _original_style = self.scan_button.styleSheet()
        self.scan_button.setStyleSheet("border: none; background: transparent;")
        
        overlay = QLabel(self.scan_button)
        overlay.setMovie(self.spinner)
        overlay.setAlignment(Qt.AlignCenter)
        overlay.setGeometry(self.scan_button.rect())
        overlay.show()
        self.spinner.start()

        timeout = self.scan_timeout_spin.value()
        try:
            devices = await self.pipeline.scan(timeout)
            devices_dict = [{"name": device.name or "Unknown", "address": device.address} for device in devices]
            self.signals.devices.emit(devices_dict)
        except Exception as e:
            print(f"Scan failed: {e}")
        finally:
            self.spinner.stop()
            overlay.hide()
            self.scan_button.setText("Scan for Devices")
            self.scan_button.setEnabled(True)
            self.scan_button.setStyleSheet(_original_style)

    def on_devices(self, devices):
        self.devices.clear()
        for device in devices:
            self.devices.addItem(f"{device['address']:17} | {device['name']}")
        self.update_gray_out()
    
    def update_gray_out(self):
        palette = self.devices.palette()
        if self.devices.count() == 0:
            palette.setColor(QPalette.Base, QColor("#f0f0f0"))
            palette.setColor(QPalette.Text, QColor("#a0a0a0"))
        else:
            palette.setColor(QPalette.Base, QColor("white"))
            palette.setColor(QPalette.Text, QColor("black"))
        self.devices.setPalette(palette)
        

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
        logger = FileLogger("monitor_data", "w")
        pipeline.register(logger.sub)

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
            tab.pipeline.close()
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