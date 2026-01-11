from PyQt6.QtWidgets import (QWidget, QHBoxLayout, QLabel, QPushButton, 
                             QApplication, QFrame)
from PyQt6.QtCore import Qt, QPoint
from PyQt6.QtGui import QIcon
import qtawesome as qta

class IconButton(QPushButton):
    def __init__(self, icon_name, hover_color=None, normal_color='#aaaaaa', parent=None):
        super().__init__(parent)
        self.icon_name = icon_name
        self.normal_color = normal_color
        self.hover_color = hover_color or normal_color
        self.update_icon(self.normal_color)
    
    def update_icon(self, color):
        self.setIcon(qta.icon(self.icon_name, color=color))

    def set_icon_name(self, icon_name):
        self.icon_name = icon_name
        self.update_icon(self.normal_color)

    def enterEvent(self, event):
        self.update_icon(self.hover_color)
        super().enterEvent(event)

    def leaveEvent(self, event):
        self.update_icon(self.normal_color)
        super().leaveEvent(event)

class CustomTitleBar(QWidget):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.parent = parent
        self.start_pos = None
        self.init_ui()

    def init_ui(self):
        self.setFixedHeight(40)
        self.setObjectName("TitleBar")
        
        layout = QHBoxLayout(self)
        layout.setContentsMargins(15, 0, 0, 0) # Zero right margin for buttons to hit edge
        layout.setSpacing(0)

        # Title
        self.title_label = QLabel("Custom RGB Controller")
        self.title_label.setObjectName("TitleLabel")
        layout.addWidget(self.title_label)

        layout.addStretch()

        # Window Controls
        # Minimize
        self.btn_min = IconButton("fa5s.window-minimize", hover_color="#ffffff", normal_color="#aaaaaa")
        self.btn_min.setObjectName("TitleBtn")
        self.btn_min.setFixedSize(46, 40)
        self.btn_min.clicked.connect(self.minimize_window)
        layout.addWidget(self.btn_min)

        # Maximize/Restore
        self.btn_max = IconButton("fa5s.square", hover_color="#ffffff", normal_color="#aaaaaa")
        self.btn_max.setObjectName("TitleBtn")
        self.btn_max.setFixedSize(46, 40)
        self.btn_max.clicked.connect(self.maximize_restore_window)
        layout.addWidget(self.btn_max)

        # Close
        self.btn_close = IconButton("fa5s.times", hover_color="#ffffff", normal_color="#aaaaaa")
        self.btn_close.setObjectName("TitleBtnClose")
        self.btn_close.setFixedSize(46, 40)
        self.btn_close.clicked.connect(self.close_window)
        layout.addWidget(self.btn_close)

    def minimize_window(self):
        if self.parent:
            self.parent.showMinimized()

    def maximize_restore_window(self):
        if self.parent:
            if self.parent.isMaximized():
                self.parent.showNormal()
                self.btn_max.set_icon_name("fa5s.square")
            else:
                self.parent.showMaximized()
                self.btn_max.set_icon_name("fa5s.window-restore")

    def close_window(self):
        if self.parent:
            # Check if tray is available (it should be on MainWindow)
            if hasattr(self.parent, 'tray_icon') and self.parent.tray_icon.isVisible():
                self.parent.hide()
            else:
                self.parent.close()

    # Mouse Events for Window Dragging
    def mousePressEvent(self, event):
        if event.button() == Qt.MouseButton.LeftButton:
            self.start_pos = event.globalPosition().toPoint()

    def mouseMoveEvent(self, event):
        if self.start_pos and self.parent:
            delta = event.globalPosition().toPoint() - self.start_pos
            self.parent.move(self.parent.pos() + delta)
            self.start_pos = event.globalPosition().toPoint()

    def mouseReleaseEvent(self, event):
        self.start_pos = None
