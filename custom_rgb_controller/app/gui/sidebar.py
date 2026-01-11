from PyQt6.QtWidgets import (QWidget, QVBoxLayout, QPushButton, QLabel, 
                             QFrame, QButtonGroup, QSpacerItem, QSizePolicy, QHBoxLayout)
from PyQt6.QtCore import Qt, pyqtSignal, QSize
import qtawesome as qta

class Sidebar(QFrame):
    page_changed = pyqtSignal(int) # Emits index of page to switch to

    def __init__(self):
        super().__init__()
        self.setObjectName("Sidebar")
        self.setFixedWidth(250)
        self.nav_buttons = [] # Store buttons to update icons later
        self.init_ui()

    def init_ui(self):
        layout = QVBoxLayout(self)
        layout.setContentsMargins(0, 20, 0, 20)
        layout.setSpacing(8)

        # App Logo/Title
        logo_layout = QHBoxLayout()
        logo_layout.setContentsMargins(20, 0, 20, 20)
        
        self.logo_icon = QLabel()
        self.logo_icon.setPixmap(qta.icon("fa5s.palette", color="#007acc").pixmap(28, 28))
        logo_layout.addWidget(self.logo_icon)
        
        self.logo_text = QLabel("RGB CONTROL")
        self.logo_text.setStyleSheet("font-size: 12pt; font-weight: 700; color: #e0e0e0; letter-spacing: 1px; font-family: 'Segoe UI';")
        logo_layout.addWidget(self.logo_text)
        logo_layout.addStretch()
        
        layout.addLayout(logo_layout)

        self.btn_group = QButtonGroup(self)
        self.btn_group.setExclusive(True)
        self.btn_group.idClicked.connect(self.on_btn_clicked)

        # Home
        self.add_nav_btn("Home", 0, "fa5s.home", checked=True)
        
        # Workshop Category
        self.add_category("Workshop")
        self.add_nav_btn("Surface Editor", 1, "fa5s.pen")
        self.add_nav_btn("Profiles", 2, "fa5s.layer-group")
        self.add_nav_btn("Devices", 3, "fa5s.desktop")

        # Settings Category
        self.add_category("General")
        self.add_nav_btn("Settings", 4, "fa5s.cog")

        layout.addStretch()

        # Footer / Version info could go here
        version = QLabel("v0.2.0")
        version.setStyleSheet("color: #666; padding-left: 20px; font-size: 8pt;")
        layout.addWidget(version)

    def add_category(self, title):
        sep = QFrame()
        sep.setObjectName("NavSeparator")
        sep.setFixedHeight(1)
        self.layout().addWidget(sep)

        label = QLabel(title)
        label.setObjectName("NavCategory")
        self.layout().addWidget(label)

    def add_nav_btn(self, text, index, icon_name=None, checked=False):
        btn = QPushButton(text)
        btn.setCheckable(True)
        btn.setChecked(checked)
        btn.setObjectName("NavButton")
        btn.setCursor(Qt.CursorShape.PointingHandCursor)
        
        if icon_name:
            # Store icon name for updates
            btn.setProperty("icon_name", icon_name)
            self.update_btn_icon(btn, icon_name, "Dark") # Default to Dark
            btn.setIconSize(QSize(20, 20))
        
        self.layout().addWidget(btn)
        self.btn_group.addButton(btn, index)
        self.nav_buttons.append(btn)

    def update_btn_icon(self, btn, icon_name, theme_name):
        if theme_name == "Light":
            color = "#666666"
            color_active = "#333333"
        else: # Dark
            color = "#cccccc"
            color_active = "#ffffff"
            
        icon = qta.icon(icon_name, color=color, color_active=color_active)
        btn.setIcon(icon)

    def update_theme(self, theme_name):
        # Update Nav Buttons
        for btn in self.nav_buttons:
            icon_name = btn.property("icon_name")
            if icon_name:
                self.update_btn_icon(btn, icon_name, theme_name)

        # Update Branding
        if theme_name == "Light":
            text_color = "#333333"
            # Keep accent color or make it match the theme's text if desired, 
            # but usually logo branding stays consistent or goes dark.
            icon_color = "#007acc" 
        else:
            text_color = "#e0e0e0"
            icon_color = "#007acc"

        self.logo_text.setStyleSheet(f"font-size: 12pt; font-weight: 700; color: {text_color}; letter-spacing: 1px; font-family: 'Segoe UI';")
        self.logo_icon.setPixmap(qta.icon("fa5s.palette", color=icon_color).pixmap(28, 28))

    def on_btn_clicked(self, index):
        self.page_changed.emit(index)
