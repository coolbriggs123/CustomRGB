from PyQt6.QtWidgets import QStackedWidget, QWidget, QLabel
from PyQt6.QtCore import Qt, QPropertyAnimation, QParallelAnimationGroup, QPoint, QEasingCurve
from PyQt6.QtGui import QPixmap

class AnimatedStackedWidget(QStackedWidget):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.m_speed = 300
        self.m_animation_type = "slide"  # slide, fade
        self.m_active = False

    def setSpeed(self, speed):
        self.m_speed = speed

    def setAnimation(self, animation_type):
        self.m_animation_type = animation_type

    def slideInIdx(self, index):
        if self.m_active:
            return
            
        if index == self.currentIndex():
            return
            
        if index < 0 or index >= self.count():
            return

        _now = self.currentWidget()
        _next = self.widget(index)
        
        if not _now or not _next:
            self.setCurrentIndex(index)
            return
            
        self.m_active = True
        
        # Geometry
        width = self.frameRect().width()
        height = self.frameRect().height()
        
        # Ensure _next has correct size before grab (if it was never shown)
        _next.resize(width, height)
        # Force layout update if needed
        # _next.updateGeometry() 
        
        # Create screenshots
        pix_now = _now.grab()
        pix_next = _next.grab()
        
        # Create overlay labels
        self.lbl_now = QLabel(self)
        self.lbl_now.setPixmap(pix_now)
        self.lbl_now.resize(width, height)
        self.lbl_now.show()
        
        self.lbl_next = QLabel(self)
        self.lbl_next.setPixmap(pix_next)
        self.lbl_next.resize(width, height)
        self.lbl_next.show()
        
        # Hide the underlying widget so it doesn't show through the transparent screenshots
        _now.hide()
        
        # Determine direction
        offset_x = width
        if index < self.currentIndex():
            offset_x = -width
            
        # Initial positions
        self.lbl_now.move(0, 0)
        self.lbl_next.move(offset_x, 0)
        
        # Prepare Animation
        self.anim_group = QParallelAnimationGroup()
        
        anim_now = QPropertyAnimation(self.lbl_now, b"pos")
        anim_now.setDuration(self.m_speed)
        anim_now.setEasingCurve(QEasingCurve.Type.OutCubic)
        anim_now.setStartValue(QPoint(0, 0))
        anim_now.setEndValue(QPoint(-offset_x, 0))
        
        anim_next = QPropertyAnimation(self.lbl_next, b"pos")
        anim_next.setDuration(self.m_speed)
        anim_next.setEasingCurve(QEasingCurve.Type.OutCubic)
        anim_next.setStartValue(QPoint(offset_x, 0))
        anim_next.setEndValue(QPoint(0, 0))
        
        self.anim_group.addAnimation(anim_now)
        self.anim_group.addAnimation(anim_next)
        
        self.anim_group.finished.connect(lambda: self.animationDone(index))
        self.anim_group.start()
        
        # Hide actual widgets during animation? 
        # Actually QStackedWidget still shows _now.
        # But our lbl_now covers it.
        # We should NOT switch page yet.

    def animationDone(self, index):
        self.setCurrentIndex(index)
        
        self.lbl_now.hide()
        self.lbl_next.hide()
        self.lbl_now.deleteLater()
        self.lbl_next.deleteLater()
        
        self.m_active = False
