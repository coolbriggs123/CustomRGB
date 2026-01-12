from PyQt6.QtWidgets import (QWidget, QVBoxLayout, QHBoxLayout, QListWidget, 
                             QPushButton, QLabel, QComboBox, QFormLayout, 
                             QSpinBox, QDoubleSpinBox, QGroupBox, QLineEdit, QColorDialog,
                             QFileDialog, QMessageBox, QInputDialog, QMenu, QGraphicsOpacityEffect)
from PyQt6.QtGui import QAction
from PyQt6.QtCore import Qt, pyqtSignal, QTimer, QPropertyAnimation, QEasingCurve
from PyQt6.QtGui import QColor
import json
import time

from app.creator.engine import CreatorEffect
from app.creator.nodes import NODE_TYPES, NODE_CLASSES, NODE_CATEGORIES
from app.gui.visualizer import VisualizerWidget
from app.core.profiles import ProfileManager

class CreatorWidget(QWidget):
    effect_updated = pyqtSignal() # Signal to notify main window to refresh
    profile_saved = pyqtSignal()
    
    def __init__(self, creator_effect):
        super().__init__()
        self.creator_effect = creator_effect
        self.profile_manager = ProfileManager()
        self.init_ui()
        
        # Setup Visualizer Timer
        self.vis_timer = QTimer()
        self.vis_timer.timeout.connect(self.update_visualizer)
        self.vis_timer.start(33) # ~30fps
        
    def init_ui(self):
        layout = QHBoxLayout(self)
        
        # Left: Layer List
        layer_group = QGroupBox("Layers (Processed Top to Bottom)")
        layer_layout = QVBoxLayout(layer_group)
        
        # File Operations
        file_layout = QHBoxLayout()
        save_btn = QPushButton("Save Effect")
        save_btn.clicked.connect(self.save_effect)
        file_layout.addWidget(save_btn)
        
        load_btn = QPushButton("Load Effect")
        load_btn.clicked.connect(self.load_effect)
        file_layout.addWidget(load_btn)
        layer_layout.addLayout(file_layout)
        
        self.layer_list = QListWidget()
        self.layer_list.currentRowChanged.connect(self.on_layer_selected)
        layer_layout.addWidget(self.layer_list)
        
        # Layer Control Buttons
        move_layout = QHBoxLayout()
        up_btn = QPushButton("Move Up")
        up_btn.clicked.connect(self.move_layer_up)
        move_layout.addWidget(up_btn)
        
        down_btn = QPushButton("Move Down")
        down_btn.clicked.connect(self.move_layer_down)
        move_layout.addWidget(down_btn)
        layer_layout.addLayout(move_layout)
        
        btn_layout = QHBoxLayout()
        
        add_btn = QPushButton("Add Node")
        add_btn.setObjectName("PrimaryButton")
        
        # Create Menu with Categories
        add_menu = QMenu(self)
        # Force the menu to not close immediately if we want? No, standard behavior is fine.
        # But user said "flay out the the right". Submenus do that automatically.
        
        for category, nodes in NODE_CATEGORIES.items():
            sub_menu = add_menu.addMenu(category)
            for node_name in nodes:
                action = sub_menu.addAction(node_name)
                action.triggered.connect(lambda checked, n=node_name: self.add_layer_by_name(n))
        
        add_btn.setMenu(add_menu)
        btn_layout.addWidget(add_btn)
        
        del_btn = QPushButton("Remove")
        del_btn.clicked.connect(self.remove_layer)
        btn_layout.addWidget(del_btn)
        
        layer_layout.addLayout(btn_layout)
        
        # Visualizer in Left Column
        self.visualizer = VisualizerWidget()
        layer_layout.addWidget(self.visualizer)
        
        layout.addWidget(layer_group, 1)
        
        # Right: Properties
        self.prop_group = QGroupBox("Layer Properties")
        self.prop_layout = QFormLayout(self.prop_group)
        layout.addWidget(self.prop_group, 1)
        
        self.refresh_layer_list()

    def animate_properties_fade_in(self):
        # Create effect specifically for animation
        self.prop_opacity = QGraphicsOpacityEffect(self.prop_group)
        self.prop_group.setGraphicsEffect(self.prop_opacity)
        
        self.anim = QPropertyAnimation(self.prop_opacity, b"opacity")
        self.anim.setDuration(300)
        self.anim.setStartValue(0.0)
        self.anim.setEndValue(1.0)
        self.anim.setEasingCurve(QEasingCurve.Type.OutQuad)
        self.anim.finished.connect(self.on_fade_in_finished)
        self.anim.start()

    def on_fade_in_finished(self):
        # Remove effect to prevent rendering issues (invisible on hover)
        self.prop_group.setGraphicsEffect(None)

    def update_theme(self, theme_name):
        self.visualizer.update_theme(theme_name)
        # Update other custom styles if needed
        # Standard widgets (QGroupBox, QPushButton, etc.) are handled by global stylesheet
        # but if we have specific hardcoded colors, we should update them here.
        pass

    def save_effect(self):
        name, ok = QInputDialog.getText(self, "Save Profile", "Enter profile name:")
        if ok and name:
            try:
                data = self.creator_effect.to_dict()
                self.profile_manager.save_profile(name, data)
                self.profile_saved.emit()
                QMessageBox.information(self, "Success", f"Profile '{name}' saved successfully!")
            except Exception as e:
                QMessageBox.critical(self, "Error", f"Failed to save profile: {e}")

    def load_effect(self):
        profiles = self.profile_manager.list_profiles()
        if not profiles:
            QMessageBox.information(self, "Load Profile", "No profiles found.")
            return

        name, ok = QInputDialog.getItem(self, "Load Profile", "Select profile:", profiles, 0, False)
        if ok and name:
            try:
                data = self.profile_manager.load_profile(name)
                if data:
                    self.load_data(data)
                    QMessageBox.information(self, "Success", f"Profile '{name}' loaded successfully!")
            except Exception as e:
                QMessageBox.critical(self, "Error", f"Failed to load profile: {e}")

    def load_data(self, data):
        self.creator_effect.load_from_dict(data, NODE_CLASSES)
        self.refresh_layer_list()
        self.clear_properties()
        
    def update_visualizer(self):
        # Render a preview frame locally
        # Use a dummy LED count of 50 for preview
        dummy_leds = [(0, 0, 0)] * 50
        # Create a context similar to the real engine
        # We need 'keys' which we can't easily get here without input hooks,
        # but for visualizer we can assume empty or maybe mock it?
        # For now, keys will be empty in preview unless we hook keyboard
        rendered = self.creator_effect.render(dummy_leds, time.time())
        self.visualizer.update_data(rendered)

    def refresh_layer_list(self):
        current = self.layer_list.currentRow()
        self.layer_list.clear()
        
        # Filter out nodes that are not in our list of nodes
        valid_layers = []
        for layer in self.creator_effect.layers:
            if type(layer) in NODE_TYPES.values():
                valid_layers.append(layer)
                self.layer_list.addItem(layer.name)
        
        # Update the effect layers to only include valid ones
        if len(valid_layers) != len(self.creator_effect.layers):
            self.creator_effect.layers = valid_layers

        if current >= 0 and current < self.layer_list.count():
            self.layer_list.setCurrentRow(current)
            
    def move_layer_up(self):
        row = self.layer_list.currentRow()
        if row > 0:
            self.creator_effect.layers[row], self.creator_effect.layers[row-1] = \
                self.creator_effect.layers[row-1], self.creator_effect.layers[row]
            self.refresh_layer_list()
            self.layer_list.setCurrentRow(row - 1)
            
    def move_layer_down(self):
        row = self.layer_list.currentRow()
        if row >= 0 and row < len(self.creator_effect.layers) - 1:
            self.creator_effect.layers[row], self.creator_effect.layers[row+1] = \
                self.creator_effect.layers[row+1], self.creator_effect.layers[row]
            self.refresh_layer_list()
            self.layer_list.setCurrentRow(row + 1)
            
    def add_layer_by_name(self, type_name):
        layer_class = NODE_TYPES.get(type_name)
        if layer_class:
            layer = layer_class()
            self.creator_effect.add_layer(layer)
            self.refresh_layer_list()
            self.layer_list.setCurrentRow(len(self.creator_effect.layers) - 1)
            
    def remove_layer(self):
        row = self.layer_list.currentRow()
        if row >= 0:
            self.creator_effect.layers.pop(row)
            self.refresh_layer_list()
            self.clear_properties()
            
    def on_layer_selected(self, row):
        self.clear_properties()
        if row < 0 or row >= len(self.creator_effect.layers):
            return
            
        layer = self.creator_effect.layers[row]
        
        # Build dynamic UI based on params
        for key, value in layer.params.items():
            label = QLabel(key.title().replace("_", " "))
            widget = None
            
            if isinstance(value, bool):
                widget = QComboBox()
                widget.addItems(["False", "True"])
                widget.setCurrentIndex(1 if value else 0)
                widget.currentTextChanged.connect(lambda t, k=key, l=layer: self.update_bool(l, k, t))
                
            elif isinstance(value, int):
                widget = QSpinBox()
                widget.setRange(0, 9999)
                widget.setValue(value)
                widget.valueChanged.connect(lambda v, k=key, l=layer: l.set_param(k, v))
                
            elif isinstance(value, float):
                widget = QDoubleSpinBox()
                widget.setRange(-9999.0, 9999.0)
                widget.setSingleStep(0.1)
                
                # Heuristics for better UX
                if key in ['opacity', 'smoothing', 'threshold', 'duty_cycle', 'persistence', 'width']:
                     widget.setRange(0.0, 1.0)
                     widget.setSingleStep(0.05)
                elif key in ['offset']:
                     widget.setRange(-10.0, 10.0) # Offset can sometimes go negative or > 1 depending on usage, but 0-1 is typical
                     widget.setSingleStep(0.05)
                
                widget.setValue(value)
                widget.valueChanged.connect(lambda v, k=key, l=layer: l.set_param(k, v))
                
            elif isinstance(value, str):
                widget = QLineEdit(value)
                widget.textChanged.connect(lambda t, k=key, l=layer: l.set_param(k, t))
                
            elif isinstance(value, (tuple, list)):
                # Check for Enum tuple (current, [options])
                if len(value) == 2 and isinstance(value[1], list):
                    current_val, options = value
                    widget = QComboBox()
                    widget.addItems(options)
                    widget.setCurrentText(current_val)
                    widget.currentTextChanged.connect(lambda t, k=key, l=layer, opts=options: self.update_enum(l, k, t, opts))
                
                # Check for Color tuple (r, g, b)
                elif len(value) == 3 and all(isinstance(x, (int, float)) for x in value):
                    widget = QPushButton(f"RGB{tuple(value)}")
                    c = QColor(*value)
                    widget.setStyleSheet(f"background-color: {c.name()}; color: {'white' if c.lightness() < 128 else 'black'};")
                    widget.clicked.connect(lambda _, k=key, l=layer, w=widget: self.pick_color(l, k, w))
                
            if widget:
                self.prop_layout.addRow(label, widget)
        
        self.animate_properties_fade_in()
                
    def clear_properties(self):
        while self.prop_layout.count():
            item = self.prop_layout.takeAt(0)
            if item.widget():
                item.widget().deleteLater()
                
    def update_bool(self, layer, key, text):
        layer.set_param(key, text == "True")
        
    def update_enum(self, layer, key, text, options):
        # Store back as (selected, options) to preserve the list
        layer.set_param(key, (text, options))
        
    def pick_color(self, layer, key, btn):
        current = layer.params[key]
        c = QColorDialog.getColor(QColor(*current))
        if c.isValid():
            rgb = (c.red(), c.green(), c.blue())
            layer.set_param(key, rgb)
            btn.setText(f"RGB{rgb}")
            btn.setStyleSheet(f"background-color: {c.name()}; color: {'white' if c.lightness() < 128 else 'black'};")
