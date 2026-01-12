from PyQt6.QtWidgets import (QWidget, QVBoxLayout, QHBoxLayout, QListWidget, 
                             QPushButton, QLabel, QMessageBox, QInputDialog, QListWidgetItem)
from PyQt6.QtCore import Qt, pyqtSignal, QSize
import json
import qtawesome as qta
from app.core.profiles import ProfileManager

class ProfilesPage(QWidget):
    profile_loaded = pyqtSignal(dict) # Emits the profile data

    def __init__(self, global_settings, save_callback):
        super().__init__()
        self.manager = ProfileManager()
        self.global_settings = global_settings
        self.save_callback = save_callback
        self.init_ui()

    def init_ui(self):
        layout = QVBoxLayout(self)
        layout.setContentsMargins(20, 20, 20, 20)
        
        title = QLabel("Profile Management")
        title.setStyleSheet("font-size: 24px; font-weight: bold; margin-bottom: 20px;")
        layout.addWidget(title)
        
        # Profile List
        self.list_widget = QListWidget()
        self.list_widget.setStyleSheet("font-size: 14px; padding: 5px;")
        layout.addWidget(self.list_widget)
        
        # Buttons
        btn_layout = QHBoxLayout()
        
        load_btn = QPushButton("Load Profile")
        load_btn.setObjectName("PrimaryButton")
        load_btn.clicked.connect(self.load_selected)
        btn_layout.addWidget(load_btn)
        
        refresh_btn = QPushButton("Refresh List")
        refresh_btn.clicked.connect(self.refresh_list)
        btn_layout.addWidget(refresh_btn)
        
        delete_btn = QPushButton("Delete Profile")
        delete_btn.setStyleSheet("background-color: #a00; color: white; border: 1px solid #800;")
        delete_btn.clicked.connect(self.delete_selected)
        btn_layout.addWidget(delete_btn)
        
        layout.addLayout(btn_layout)
        
        self.refresh_list()

    def refresh_list(self):
        self.list_widget.clear()
        profiles = self.manager.list_profiles()
        fav_profile = self.global_settings.get('favorite_profile')

        for p_name in profiles:
            item = QListWidgetItem(self.list_widget)
            item.setSizeHint(QSize(0, 50))
            
            # Custom Widget
            widget = QWidget()
            w_layout = QHBoxLayout(widget)
            w_layout.setContentsMargins(10, 0, 10, 0)
            
            # Name
            name_lbl = QLabel(p_name)
            name_lbl.setStyleSheet("font-size: 14px;")
            w_layout.addWidget(name_lbl)
            
            w_layout.addStretch()
            
            # Star Button
            star_btn = QPushButton()
            star_btn.setFixedSize(30, 30)
            star_btn.setCursor(Qt.CursorShape.PointingHandCursor)
            
            is_fav = (p_name == fav_profile)
            
            # Use "fa5s.star" for both but change color to indicate state
            # This avoids the "Invalid font prefix fa5r" error if the regular font isn't loaded
            icon_name = "fa5s.star"
            color = "#ffc107" if is_fav else "#444444"
            
            star_btn.setIcon(qta.icon(icon_name, color=color))
            star_btn.setStyleSheet("background: transparent; border: none;")
            star_btn.clicked.connect(lambda checked, n=p_name: self.toggle_favorite(n))
            
            w_layout.addWidget(star_btn)
            
            self.list_widget.setItemWidget(item, widget)

    def toggle_favorite(self, name):
        current_fav = self.global_settings.get('favorite_profile')
        if current_fav == name:
            # Unfavorite if clicking the same one
            self.global_settings['favorite_profile'] = None
        else:
            self.global_settings['favorite_profile'] = name
            
        if self.save_callback:
            self.save_callback()
            
        self.refresh_list()

    def load_selected(self):
        item = self.list_widget.currentItem()
        if not item:
            return
            
        # Retrieve name from the custom widget
        widget = self.list_widget.itemWidget(item)
        if widget:
            # The first child layout widget is the label
            name_lbl = widget.findChild(QLabel)
            if name_lbl:
                name = name_lbl.text()
                self._load_profile_by_name(name)

    def _load_profile_by_name(self, name):
        try:
            data = self.manager.load_profile(name)
            if data:
                self.profile_loaded.emit(data)
                QMessageBox.information(self, "Success", f"Profile '{name}' loaded!")
        except Exception as e:
            QMessageBox.critical(self, "Error", f"Failed to load profile: {e}")

    def delete_selected(self):
        item = self.list_widget.currentItem()
        if not item:
            return
            
        widget = self.list_widget.itemWidget(item)
        if not widget:
            return
            
        name_lbl = widget.findChild(QLabel)
        if not name_lbl:
            return
            
        name = name_lbl.text()
        confirm = QMessageBox.question(self, "Confirm Delete", 
                                     f"Are you sure you want to delete '{name}'?",
                                     QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No)
        
        if confirm == QMessageBox.StandardButton.Yes:
            try:
                self.manager.delete_profile(name)
                self.refresh_list()
            except Exception as e:
                QMessageBox.critical(self, "Error", f"Failed to delete profile: {e}")
