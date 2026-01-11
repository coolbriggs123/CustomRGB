from PyQt6.QtWidgets import QWidget
from PyQt6.QtCore import Qt, QPointF
from PyQt6.QtGui import QPainter, QColor, QBrush, QPen, QRadialGradient, QLinearGradient

class VisualizerWidget(QWidget):
    def __init__(self, led_count=50):
        super().__init__()
        self.setMinimumHeight(120)
        self.led_colors = [(0, 0, 0)] * led_count
        self.led_count = led_count
        self.setAutoFillBackground(True)
        self.update_theme("Dark") # Default
        
    def update_theme(self, theme_name):
        self.theme_name = theme_name
        p = self.palette()
        if theme_name == "Light":
            p.setColor(self.backgroundRole(), QColor("#f0f0f0"))
        else:
            p.setColor(self.backgroundRole(), QColor("#1e1e1e"))
        self.setPalette(p)
        self.update()

    def update_data(self, colors):
        """
        colors: list of (r, g, b) tuples
        """
        self.led_colors = colors
        self.led_count = len(colors)
        self.update() # Trigger paintEvent

    def paintEvent(self, event):
        painter = QPainter(self)
        painter.setRenderHint(QPainter.RenderHint.Antialiasing)
        
        w = self.width()
        h = self.height()
        
        # Draw Background Track/Casing
        track_height = 50
        track_y = (h - track_height) / 2
        
        # Outer casing with gradient
        track_grad = QLinearGradient(0, track_y, 0, track_y + track_height)
        if hasattr(self, 'theme_name') and self.theme_name == "Light":
            track_grad.setColorAt(0, QColor("#e0e0e0"))
            track_grad.setColorAt(0.2, QColor("#ffffff"))
            track_grad.setColorAt(0.8, QColor("#ffffff"))
            track_grad.setColorAt(1, QColor("#e0e0e0"))
        else:
            track_grad.setColorAt(0, QColor("#333333"))
            track_grad.setColorAt(0.2, QColor("#1a1a1a"))
            track_grad.setColorAt(0.8, QColor("#1a1a1a"))
            track_grad.setColorAt(1, QColor("#333333"))
        
        painter.setPen(Qt.PenStyle.NoPen)
        painter.setBrush(QBrush(track_grad))
        painter.drawRoundedRect(10, int(track_y), int(w - 20), int(track_height), 10, 10)
        
        if self.led_count == 0:
            return
            
        # Calculate LED Geometry
        # We want to fit 'led_count' LEDs into 'w - 40' space.
        # space_per_led = (w - 40) / led_count
        # We want some padding. Let's say padding is 20% of space_per_led, but max 6px.
        
        available_w = w - 40
        if available_w <= 0:
            return

        space_per_led = available_w / self.led_count
        
        # Calculate padding and size dynamically
        padding = min(6, space_per_led * 0.3)
        led_size = space_per_led - padding
        
        # Clamp max size
        if led_size > 30:
            led_size = 30
            padding = 6 # Reset padding to standard if we are hitting max size
            
        # If LEDs are super tiny, we might just have to deal with it or draw simple rects
        # But let's keep min size reasonable, but strictly enforce fit?
        # If we enforce min size 4, and it doesn't fit, we overflow.
        # Better to scale down or overlap? Addressable strips usually don't overlap.
        # Let's allow them to get very small if needed, but < 2 is invisible.
        led_size = max(1, led_size)
        
        # Recalculate total used width based on final size
        # We center the actual used width
        total_content_w = (led_size + padding) * self.led_count - padding # Remove last padding
        
        start_x = (w - total_content_w) / 2
        led_y = h / 2
        
        for i, color in enumerate(self.led_colors):
            r, g, b = color
            # Center of this LED slot
            center_x = start_x + i * (led_size + padding) + led_size / 2
            
            # 1. Draw Glow (if lit)
            # Clip glow to widget bounds if needed, but QPainter clips automatically to widget rect.
            # If we want to clip to "Track", we can set a clip path.
            # But usually glow extends.
            if r > 20 or g > 20 or b > 20:
                glow_radius = led_size * 2.5
                glow = QRadialGradient(QPointF(center_x, led_y), glow_radius)
                glow.setColorAt(0, QColor(r, g, b, 120))
                glow.setColorAt(0.5, QColor(r, g, b, 30))
                glow.setColorAt(1, QColor(r, g, b, 0))
                
                painter.setBrush(QBrush(glow))
                painter.drawEllipse(QPointF(center_x, led_y), glow_radius, glow_radius)

            # 2. Draw LED Body
            # Base color (dimmer version of light)
            base_color = QColor(max(20, int(r*0.8)), max(20, int(g*0.8)), max(20, int(b*0.8)))
            painter.setBrush(QBrush(base_color))
            painter.drawEllipse(QPointF(center_x, led_y), led_size/2, led_size/2)
            
            if led_size > 4: # Only draw reflection if large enough
                # 3. Draw Hotspot/Reflection (shiny plastic look)
                shine_grad = QRadialGradient(QPointF(center_x - led_size*0.15, led_y - led_size*0.15), led_size/2)
                shine_grad.setColorAt(0, QColor(255, 255, 255, 200))
                shine_grad.setColorAt(1, QColor(255, 255, 255, 0))
                
                painter.setBrush(QBrush(shine_grad))
                painter.drawEllipse(QPointF(center_x, led_y), led_size/2, led_size/2)

