from PyQt6.QtWidgets import (QWidget, QVBoxLayout, QHBoxLayout, QLabel, 
                             QPushButton, QScrollArea, QFrame, QGridLayout)
from PyQt6.QtCore import Qt, QTimer

class DeviceCard(QFrame):
    def __init__(self, index, name, led_count, identify_callback):
        super().__init__()
        self.index = index
        self.identify_callback = identify_callback
        self.setObjectName("DeviceCard")
        self.update_theme("Dark") # Default to Dark
        
        layout = QHBoxLayout(self)
        
        info_layout = QVBoxLayout()
        self.name_lbl = QLabel(name)
        self.name_lbl.setObjectName("DeviceName")
        self.count_lbl = QLabel(f"{led_count} LEDs")
        self.count_lbl.setObjectName("DeviceCount")
        
        info_layout.addWidget(self.name_lbl)
        info_layout.addWidget(self.count_lbl)
        
        layout.addLayout(info_layout)
        layout.addStretch()
        
        self.id_btn = QPushButton("Identify")
        self.id_btn.setCheckable(True)
        self.id_btn.clicked.connect(self.on_identify)
        layout.addWidget(self.id_btn)

    def update_theme(self, theme_name):
        if theme_name == "Light":
            bg_color = "#ffffff"
            border_color = "#cccccc"
            text_color = "#000000"
            subtext_color = "#666666"
        else:
            bg_color = "#2d2d30"
            border_color = "#3e3e42"
            text_color = "#ffffff"
            subtext_color = "#888888"

        self.setStyleSheet(f"""
            QFrame#DeviceCard {{
                background-color: {bg_color};
                border: 1px solid {border_color};
                border-radius: 6px;
            }}
            QLabel#DeviceName {{
                color: {text_color};
                font-weight: bold;
                font-size: 14px;
            }}
            QLabel#DeviceCount {{
                color: {subtext_color};
            }}
        """)
        
    def on_identify(self, checked):
        if checked:
            self.id_btn.setText("Identifying...")
            self.identify_callback(self.index)
        else:
            self.id_btn.setText("Identify")
            self.identify_callback(-1)
            
    def reset(self):
        self.id_btn.setChecked(False)
        self.id_btn.setText("Identify")

class DevicesPage(QWidget):
    def __init__(self, backend, global_settings):
        super().__init__()
        self.backend = backend
        self.global_settings = global_settings
        self.cards = []
        self.init_ui()
        
    def init_ui(self):
        layout = QVBoxLayout(self)
        layout.setContentsMargins(20, 20, 20, 20)
        
        self.title = QLabel("Connected Devices")
        self.title.setObjectName("PageTitle")
        # Style will be set by update_theme or global stylesheet
        layout.addWidget(self.title)
        
        scroll = QScrollArea()
        scroll.setWidgetResizable(True)
        scroll.setStyleSheet("background: transparent; border: none;")
        
        content = QWidget()
        content.setStyleSheet("background: transparent;")
        self.grid = QVBoxLayout(content)
        self.grid.setAlignment(Qt.AlignmentFlag.AlignTop)
        self.grid.setSpacing(10)
        
        self.populate_devices()
        
        scroll.setWidget(content)
        layout.addWidget(scroll)

    def update_theme(self, theme_name):
        # Update title color
        if theme_name == "Light":
            self.title.setStyleSheet("font-size: 24px; font-weight: bold; margin-bottom: 20px; color: #000000;")
        else:
            self.title.setStyleSheet("font-size: 24px; font-weight: bold; margin-bottom: 20px; color: #ffffff;")
            
        # Update all cards
        for card in self.cards:
            card.update_theme(theme_name)
        
    def populate_devices(self):
        # Clear existing
        for i in reversed(range(self.grid.count())): 
            self.grid.itemAt(i).widget().setParent(None)
        self.cards = []
            
        if not self.backend or not hasattr(self.backend, 'client'):
            # Mock devices if no backend
            mock_devices = [
                ("Mock Keyboard", 104),
                ("Mock Mouse", 12),
                ("Mock Motherboard", 20)
            ]
            for i, (name, count) in enumerate(mock_devices):
                self.add_device_card(i, name, count)
            return

        try:
            for i, device in enumerate(self.backend.client.devices):
                self.add_device_card(i, device.name, len(device.leds))
        except Exception as e:
            lbl = QLabel(f"Error loading devices: {e}")
            lbl.setStyleSheet("color: red;")
            self.grid.addWidget(lbl)
            
    def add_device_card(self, index, name, count):
        card = DeviceCard(index, name, count, self.handle_identify)
        self.grid.addWidget(card)
        self.cards.append(card)
        
    def handle_identify(self, index):
        # Reset other buttons if a new one is checked
        if index != -1:
            for card in self.cards:
                if card.index != index and card.id_btn.isChecked():
                    card.reset()
        
        self.global_settings['identify_device'] = index
