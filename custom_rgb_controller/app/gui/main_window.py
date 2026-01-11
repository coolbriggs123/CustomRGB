import sys
import threading
import json
import os
import time
from PyQt6.QtWidgets import (QApplication, QMainWindow, QWidget, QVBoxLayout, 
                             QHBoxLayout, QPushButton, QLabel, QStackedWidget,
                             QFrame, QSlider, QListWidget, QGroupBox, QMessageBox,
                             QGraphicsDropShadowEffect, QSystemTrayIcon, QMenu)
from PyQt6.QtCore import Qt
from PyQt6.QtGui import QKeyEvent, QColor, QAction, QCloseEvent
import qtawesome as qta

try:
    from app.backend.openrgb_backend import OpenRGBBackend
except ImportError:
    OpenRGBBackend = None

from app.creator.engine import CreatorEffect
from app.gui.creator_widget import CreatorWidget
from app.gui.title_bar import CustomTitleBar
from app.gui.sidebar import Sidebar
from app.gui.styles import ARTEMIS_STYLESHEET, get_stylesheet
from app.engine.renderer import render_loop
from app.gui.devices_page import DevicesPage
from app.gui.profiles_page import ProfilesPage
from app.gui.settings_page import SettingsPage
from app.path_utils import get_app_root

class NullBackend:
    def push_frame(self, frame):
        return

class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Custom RGB Controller")
        self.resize(1280, 850)
        
        # Frameless and Transparent
        self.setWindowFlags(Qt.WindowType.FramelessWindowHint)
        self.setAttribute(Qt.WidgetAttribute.WA_TranslucentBackground)
        
        # Apply Artemis stylesheet
        self.setStyleSheet(ARTEMIS_STYLESHEET)
        
        # Load Settings
        self.load_settings()
        
        # Backend setup
        self.init_backend()
        
        # Initial effect (Creator Mode Only)
        self.creator_effect = CreatorEffect() 
        self.effects = [self.creator_effect]
        
        # Start rendering thread
        self.render_thread = threading.Thread(
            target=render_loop, 
            args=(self.leds, self.effects, self.backend, self.global_settings), 
            daemon=True
        )
        self.render_thread.start()
        
        self.init_ui()
        self.init_tray()
        
        # Apply initial theme
        self.on_theme_changed(self.global_settings.get('theme', 'Dark'))

    def load_settings(self):
        self.settings_file = os.path.join(get_app_root(), 'settings.json')
        default_settings = {
            'brightness': 1.0, 
            'identify_device': -1,
            'fps_limit': 60,
            'minimize_to_tray': True,
            'start_minimized': False,
            'auto_connect': True,
            'openrgb_host': '127.0.0.1',
            'openrgb_port': 6742,
            'theme': 'Dark'
        }
        
        if os.path.exists(self.settings_file):
            try:
                with open(self.settings_file, 'r') as f:
                    loaded = json.load(f)
                    # Merge with defaults
                    self.global_settings = {**default_settings, **loaded}
            except Exception:
                self.global_settings = default_settings
        else:
            self.global_settings = default_settings

    def save_settings(self):
        try:
            with open(self.settings_file, 'w') as f:
                json.dump(self.global_settings, f, indent=4)
        except Exception:
            pass

    def init_backend(self):
        if not OpenRGBBackend or not self.global_settings.get('auto_connect', True):
            self.leds = list(range(100))
            self.backend = NullBackend()
            return

        host = str(self.global_settings.get('openrgb_host', '127.0.0.1'))
        port = int(self.global_settings.get('openrgb_port', 6742))
        connect_host = host
        if connect_host in ("0.0.0.0", "::"):
            connect_host = "127.0.0.1"

        self.openrgb_process = OpenRGBBackend.ensure_server_running(host, port, wait_s=2.0)
        
        try:
            self.backend = OpenRGBBackend(host=connect_host, port=port)
            if hasattr(self.backend, 'get_led_map'):
                self.leds = self.backend.get_led_map()
            else:
                total_leds = sum(len(d.leds) for d in self.backend.client.devices)
                self.leds = list(range(total_leds))
            return
        except Exception:
            # Connection failed
            pass

        # If we reached here, connection failed. Check if installed.
        if not OpenRGBBackend.is_installed():
            # Prompt user
            reply = QMessageBox.question(None, "OpenRGB Not Found", 
                                         "OpenRGB was not found on your system.\n"
                                         "This app requires OpenRGB to control devices.\n\n"
                                         "Would you like to go to the download page?",
                                         QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No)
            
            if reply == QMessageBox.StandardButton.Yes:
                QDesktopServices.openUrl(QUrl("https://openrgb.org/"))
        
        # Fallback to NullBackend
        self.leds = list(range(100))
        self.backend = NullBackend()

    def init_ui(self):
        # Main Window Layout (Transparent wrapper)
        central_widget = QWidget()
        central_widget.setAttribute(Qt.WidgetAttribute.WA_TranslucentBackground)
        self.setCentralWidget(central_widget)
        
        window_layout = QVBoxLayout(central_widget)
        window_layout.setContentsMargins(10, 10, 10, 10)
        window_layout.setSpacing(0)
        
        # Main Container (Visible Frame)
        self.main_container = QFrame()
        self.main_container.setObjectName("MainContainer")
        # Stylesheet is handled by global style, but we can enforce specific props here if needed
        
        # Drop Shadow
        shadow = QGraphicsDropShadowEffect(self)
        shadow.setBlurRadius(20)
        shadow.setXOffset(0)
        shadow.setYOffset(0)
        shadow.setColor(QColor(0, 0, 0, 150))
        self.main_container.setGraphicsEffect(shadow)
        
        container_layout = QVBoxLayout(self.main_container)
        container_layout.setContentsMargins(0, 0, 0, 0)
        container_layout.setSpacing(0)
        
        # Custom Title Bar
        self.title_bar = CustomTitleBar(self)
        container_layout.addWidget(self.title_bar)
        
        # Body (Sidebar + Content)
        body_widget = QWidget()
        body_layout = QHBoxLayout(body_widget)
        body_layout.setContentsMargins(0, 0, 0, 0)
        body_layout.setSpacing(0)
        
        # Sidebar
        self.sidebar = Sidebar()
        self.sidebar.page_changed.connect(self.switch_page)
        body_layout.addWidget(self.sidebar)
        
        # Content Stack
        self.stack = QStackedWidget()
        body_layout.addWidget(self.stack)
        
        container_layout.addWidget(body_widget)
        window_layout.addWidget(self.main_container)
        
        # Pages
        self.create_pages()
        
    def create_pages(self):
        # Home Page (Placeholder)
        home_page = QWidget()
        home_layout = QVBoxLayout(home_page)
        lbl = QLabel("Welcome to Custom RGB Controller")
        lbl.setAlignment(Qt.AlignmentFlag.AlignCenter)
        lbl.setStyleSheet("font-size: 18pt; color: #666;")
        home_layout.addWidget(lbl)
        self.stack.addWidget(home_page) # 0
        
        # Workshop - Creator
        self.creator_page = CreatorWidget(self.creator_effect)
        self.creator_page.profile_saved.connect(self.on_profile_saved)
        self.stack.addWidget(self.creator_page) # 1
        
        # Profiles Page
        self.profiles_page = ProfilesPage()
        self.profiles_page.profile_loaded.connect(self.on_profile_loaded)
        self.stack.addWidget(self.profiles_page) # 2
        
        # Devices Page
        self.devices_page = DevicesPage(self.backend, self.global_settings)
        self.stack.addWidget(self.devices_page) # 3
        
        # Settings Page
        self.settings_page = SettingsPage(self.backend, self.global_settings, self.save_settings)
        self.settings_page.theme_changed.connect(self.on_theme_changed)
        self.stack.addWidget(self.settings_page) # 4
        
    def on_theme_changed(self, theme_name):
        new_stylesheet = get_stylesheet(theme_name)
        self.setStyleSheet(new_stylesheet)
        self.sidebar.update_theme(theme_name)
        if hasattr(self, 'devices_page'):
            self.devices_page.update_theme(theme_name)
        if hasattr(self, 'creator_page'):
            self.creator_page.update_theme(theme_name)
        
    def on_profile_loaded(self, data):
        self.creator_page.load_data(data)
        self.switch_page(1) # Switch to Creator tab to show loaded effect

    def on_profile_saved(self):
        # Refresh the profiles page list if it exists
        if hasattr(self, 'profiles_page'):
            self.profiles_page.refresh_list()

    def switch_page(self, index):
        self.stack.setCurrentIndex(index)

    def init_tray(self):
        self.tray_icon = QSystemTrayIcon(self)
        
        # Use a generic icon if app icon isn't set, or qtawesome
        icon = qta.icon('fa5s.lightbulb', color='#007acc')
        self.tray_icon.setIcon(icon)
        
        # Tray Menu
        tray_menu = QMenu()
        
        # Show/Hide Action
        show_action = QAction("Show", self)
        show_action.triggered.connect(self.show)
        tray_menu.addAction(show_action)
        
        hide_action = QAction("Hide", self)
        hide_action.triggered.connect(self.hide)
        tray_menu.addAction(hide_action)
        
        tray_menu.addSeparator()
        
        # Quit Action
        quit_action = QAction("Quit", self)
        quit_action.triggered.connect(self.quit_app)
        tray_menu.addAction(quit_action)
        
        self.tray_icon.setContextMenu(tray_menu)
        self.tray_icon.show()
        
        # Handle click on tray icon itself (e.g., left click to toggle)
        self.tray_icon.activated.connect(self.on_tray_activated)

    def on_tray_activated(self, reason):
        if reason == QSystemTrayIcon.ActivationReason.Trigger:
            if self.isVisible():
                self.hide()
            else:
                self.show()
                self.activateWindow()

    def quit_app(self):
        # Clean up threads if needed
        self.tray_icon.hide()
        QApplication.quit()

    def closeEvent(self, event: QCloseEvent):
        if self.global_settings.get('minimize_to_tray', True):
            event.ignore()
            self.hide()
            self.tray_icon.showMessage(
                "Custom RGB Controller",
                "Application minimized to tray. Right-click the icon to quit.",
                QSystemTrayIcon.MessageIcon.Information,
                2000
            )
        else:
            self.quit_app()

def run_app():
    app = QApplication(sys.argv)
    app.setQuitOnLastWindowClosed(False) # Important for tray only mode
    
    window = MainWindow()
    
    # Check start minimized setting
    if window.global_settings.get('start_minimized', False):
        # Don't show the window, just ensure tray is there
        pass
    else:
        window.show()
        
    sys.exit(app.exec())
