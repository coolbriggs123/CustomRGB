from PyQt6.QtWidgets import (QWidget, QVBoxLayout, QHBoxLayout, QLabel, 
                             QLineEdit, QSpinBox, QPushButton, QCheckBox, 
                             QComboBox, QGroupBox, QFormLayout, QTabWidget,
                             QSlider, QScrollArea)
from PyQt6.QtCore import Qt, pyqtSignal

class SettingsPage(QWidget):
    theme_changed = pyqtSignal(str) # Emits theme name ("Dark" or "Light")

    def __init__(self, backend, global_settings, save_callback=None):
        super().__init__()
        self.backend = backend
        self.global_settings = global_settings
        self.save_callback = save_callback
        self.init_ui()

    def init_ui(self):
        layout = QVBoxLayout(self)
        layout.setContentsMargins(20, 20, 20, 20)
        
        # Header
        header = QLabel("Settings")
        header.setObjectName("PageTitle")
        # Style set by parent/theme
        header.setStyleSheet("font-size: 24px; font-weight: bold; margin-bottom: 10px;")
        layout.addWidget(header)

        # Tabs
        self.tabs = QTabWidget()
        layout.addWidget(self.tabs)

        # Tab 1: General
        self.tabs.addTab(self.create_general_tab(), "General")
        
        # Tab 2: Connection
        self.tabs.addTab(self.create_connection_tab(), "Connection")
        
        # Tab 3: Appearance
        self.tabs.addTab(self.create_appearance_tab(), "Appearance")
        
        # Tab 4: About
        self.tabs.addTab(self.create_about_tab(), "About")

    def create_general_tab(self):
        widget = QWidget()
        layout = QVBoxLayout(widget)
        layout.setAlignment(Qt.AlignmentFlag.AlignTop)
        layout.setSpacing(20)

        # Application Behavior
        behavior_group = QGroupBox("Application Behavior")
        behavior_layout = QVBoxLayout()
        
        self.chk_start_boot = QCheckBox("Start on System Boot")
        self.chk_start_boot.setToolTip("Launch the application automatically when Windows starts.")
        
        self.chk_start_minimized = QCheckBox("Start Minimized")
        self.chk_start_minimized.setToolTip("Start the application hidden in the system tray.")
        self.chk_start_minimized.setChecked(self.global_settings.get('start_minimized', False))
        
        self.chk_tray_minimize = QCheckBox("Minimize to Tray on Close")
        self.chk_tray_minimize.setToolTip("When clicking X, minimize to tray instead of quitting.")
        self.chk_tray_minimize.setChecked(self.global_settings.get('minimize_to_tray', True))
        
        # Connect signals
        self.chk_start_minimized.stateChanged.connect(lambda s: self.update_setting('start_minimized', s == 2))
        self.chk_tray_minimize.stateChanged.connect(lambda s: self.update_setting('minimize_to_tray', s == 2))
        
        behavior_layout.addWidget(self.chk_start_boot)
        behavior_layout.addWidget(self.chk_start_minimized)
        behavior_layout.addWidget(self.chk_tray_minimize)
        behavior_group.setLayout(behavior_layout)
        layout.addWidget(behavior_group)
        
        # Performance & Output
        perf_group = QGroupBox("Performance & Output")
        perf_layout = QFormLayout()
        
        self.fps_limit = QSpinBox()
        self.fps_limit.setRange(10, 144)
        self.fps_limit.setValue(self.global_settings.get('fps_limit', 30))
        self.fps_limit.setSuffix(" FPS")
        self.fps_limit.setToolTip("Limit the LED update rate to save CPU usage.")
        self.fps_limit.valueChanged.connect(lambda v: self.update_setting('fps_limit', v))
        
        self.brightness_slider = QSlider(Qt.Orientation.Horizontal)
        self.brightness_slider.setRange(0, 100)
        self.brightness_slider.setValue(int(self.global_settings.get('brightness', 1.0) * 100))
        self.brightness_lbl = QLabel(f"{self.brightness_slider.value()}%")
        self.brightness_slider.valueChanged.connect(self.on_brightness_changed)
        
        brightness_layout = QHBoxLayout()
        brightness_layout.addWidget(self.brightness_slider)
        brightness_layout.addWidget(self.brightness_lbl)
        
        perf_layout.addRow("Target Frame Rate:", self.fps_limit)
        perf_layout.addRow("Global Brightness:", brightness_layout)
        
        perf_group.setLayout(perf_layout)
        layout.addWidget(perf_group)
        
        return widget

    def create_connection_tab(self):
        widget = QWidget()
        layout = QVBoxLayout(widget)
        layout.setAlignment(Qt.AlignmentFlag.AlignTop)
        
        conn_group = QGroupBox("OpenRGB Server Configuration")
        conn_layout = QFormLayout()
        
        self.host_input = QLineEdit(str(self.global_settings.get('openrgb_host', "127.0.0.1")))
        self.host_input.setPlaceholderText("e.g., 192.168.1.100")
        self.host_input.textChanged.connect(lambda t: self.update_setting('openrgb_host', t.strip()))
        
        self.port_input = QSpinBox()
        self.port_input.setRange(1, 65535)
        self.port_input.setValue(int(self.global_settings.get('openrgb_port', 6742)))
        self.port_input.valueChanged.connect(lambda v: self.update_setting('openrgb_port', int(v)))
        
        self.chk_auto_connect = QCheckBox("Auto-connect on Startup")
        self.chk_auto_connect.setChecked(self.global_settings.get('auto_connect', True))
        self.chk_auto_connect.stateChanged.connect(lambda s: self.update_setting('auto_connect', s == 2))
        
        self.connect_btn = QPushButton("Test Connection")
        self.connect_btn.clicked.connect(self.on_connect_clicked)
        
        conn_layout.addRow("Host IP:", self.host_input)
        conn_layout.addRow("Port:", self.port_input)
        conn_layout.addRow("", self.chk_auto_connect)
        conn_layout.addRow("", self.connect_btn)
        
        conn_group.setLayout(conn_layout)
        layout.addWidget(conn_group)
        
        help_lbl = QLabel("Note: Ensure the OpenRGB SDK Server is running on the target machine.")
        help_lbl.setWordWrap(True)
        help_lbl.setStyleSheet("color: #888; font-style: italic; margin-top: 10px;")
        layout.addWidget(help_lbl)
        
        return widget

    def create_appearance_tab(self):
        widget = QWidget()
        layout = QVBoxLayout(widget)
        layout.setAlignment(Qt.AlignmentFlag.AlignTop)
        
        app_group = QGroupBox("Theme Settings")
        app_layout = QFormLayout()
        
        self.theme_combo = QComboBox()
        self.theme_combo.addItems(["Dark (Default)", "Light"])
        self.theme_combo.currentIndexChanged.connect(self.on_theme_changed)
        
        app_layout.addRow("Interface Theme:", self.theme_combo)
        app_group.setLayout(app_layout)
        layout.addWidget(app_group)
        
        return widget

    def create_about_tab(self):
        widget = QWidget()
        layout = QVBoxLayout(widget)
        layout.setAlignment(Qt.AlignmentFlag.AlignCenter)
        
        title = QLabel("Custom RGB Controller")
        title.setStyleSheet("font-size: 20px; font-weight: bold;")
        
        version = QLabel("Version 0.2.0")
        version.setStyleSheet("color: #888; margin-bottom: 20px;")
        
        desc = QLabel("A modern, custom interface for OpenRGB.\nCreate layers, manage profiles, and control your devices.")
        desc.setAlignment(Qt.AlignmentFlag.AlignCenter)
        desc.setStyleSheet("margin-bottom: 20px;")
        
        credits = QLabel("Powered by OpenRGB SDK\nBuilt with PyQt6")
        credits.setAlignment(Qt.AlignmentFlag.AlignCenter)
        credits.setStyleSheet("color: #666;")
        
        layout.addWidget(title)
        layout.addWidget(version)
        layout.addWidget(desc)
        layout.addWidget(credits)
        layout.addStretch()
        
        return widget

    def on_brightness_changed(self, value):
        self.brightness_lbl.setText(f"{value}%")
        self.update_setting('brightness', value / 100.0)

    def on_connect_clicked(self):
        host = self.host_input.text()
        port = self.port_input.value()
        # Logic to reconnect backend would go here
        # For now, just print or show status
        _ = (host, port)
        # In a real app, we would call self.backend.connect(host, port) if supported
        
    def update_setting(self, key, value):
        self.global_settings[key] = value
        if self.save_callback:
            self.save_callback()

    def on_theme_changed(self, index):
        theme_name = self.theme_combo.currentText()
        # Handle "Dark (Default)"
        if "Dark" in theme_name:
            theme_name = "Dark"

        self.theme_changed.emit(theme_name)
        self.update_setting('theme', theme_name)
