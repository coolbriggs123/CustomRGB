# Theme Palettes
THEMES = {
    "Dark": {
        "BG_MAIN": "#121212",      # Deep dark background
        "BG_SIDEBAR": "#1e1e1e",   # Slightly lighter for sidebar
        "BG_HEADER": "#1e1e1e",    # Header matches sidebar
        "BG_CARD": "#252526",      # Card background
        "BG_INPUT": "#2d2d30",     # Input fields
        "BG_HOVER": "#333333",     # Hover state
        "BG_SELECTED": "#37373d",  # Selected state
        "ACCENT": "#007acc",       # VS Code Blue
        "ACCENT_HOVER": "#1f8ad2",
        "ACCENT_PRESSED": "#005f9e",
        "TEXT_MAIN": "#e0e0e0",    # Soft white
        "TEXT_DIM": "#aaaaaa",     # Dimmed text
        "TEXT_DISABLED": "#666666",
        "BORDER": "#333333",       # Subtle border
        "BORDER_FOCUS": "#007acc",
    },
    "Light": {
        "BG_MAIN": "#f3f3f3",
        "BG_SIDEBAR": "#e0e0e0",
        "BG_HEADER": "#e0e0e0",
        "BG_CARD": "#ffffff",
        "BG_INPUT": "#ffffff",
        "BG_HOVER": "#e8e8e8",
        "BG_SELECTED": "#d0d0d0",
        "ACCENT": "#007acc",
        "ACCENT_HOVER": "#1f8ad2",
        "ACCENT_PRESSED": "#005f9e",
        "TEXT_MAIN": "#333333",
        "TEXT_DIM": "#666666",
        "TEXT_DISABLED": "#999999",
        "BORDER": "#cccccc",
        "BORDER_FOCUS": "#007acc",
    }
}

def get_stylesheet(theme_name="Dark"):
    theme = THEMES.get(theme_name, THEMES["Dark"])
    
    return f"""
/* Global Reset */
* {{
    font-family: 'Segoe UI', 'Roboto', sans-serif;
    font-size: 10pt;
    outline: none;
}}

QMainWindow {{
    background-color: {theme['BG_MAIN']};
    color: {theme['TEXT_MAIN']};
}}

QWidget {{
    background-color: transparent;
    color: {theme['TEXT_MAIN']};
}}

/* Main Container Frame */
QFrame#MainContainer {{
    background-color: {theme['BG_MAIN']};
    border: 1px solid {theme['BORDER']};
    border-radius: 10px;
}}

/* Tooltips */
QToolTip {{
    background-color: {theme['BG_CARD']};
    color: {theme['TEXT_MAIN']};
    border: 1px solid {theme['BORDER']};
    border-radius: 4px;
    padding: 4px;
}}

/* Menus */
QMenu {{
    background-color: {theme['BG_CARD']};
    color: {theme['TEXT_MAIN']};
    border: 1px solid {theme['BORDER']};
}}

QMenu::item {{
    padding: 5px 20px 5px 20px;
    background-color: transparent;
}}

QMenu::item:selected {{
    background-color: {theme['ACCENT']};
    color: #ffffff;
}}

/* Custom Title Bar */
QWidget#TitleBar {{
    background-color: {theme['BG_HEADER']}; 
    border-bottom: 1px solid {theme['BORDER']};
    border-top-left-radius: 10px;
    border-top-right-radius: 10px;
}}

QLabel#TitleLabel {{
    color: {theme['TEXT_MAIN']};
    font-weight: 600;
    font-size: 11pt;
    padding-left: 10px;
}}

/* Window Controls */
QPushButton#TitleBtn {{
    background-color: transparent;
    border: none;
    color: {theme['TEXT_DIM']};
    border-radius: 0px;
    font-size: 11pt;
}}

QPushButton#TitleBtn:hover {{
    background-color: {theme['BG_HOVER']};
    color: {theme['TEXT_MAIN']};
}}

QPushButton#TitleBtnClose {{
    background-color: transparent;
    border: none;
    color: {theme['TEXT_DIM']};
    border-radius: 0px;
    font-size: 11pt;
    border-top-right-radius: 10px;
}}

QPushButton#TitleBtnClose:hover {{
    background-color: #e81123;
    color: white;
}}

/* Sidebar */
QFrame#Sidebar {{
    background-color: {theme['BG_SIDEBAR']};
    border-right: 1px solid {theme['BORDER']};
    border-bottom-left-radius: 10px;
}}

QPushButton#NavButton {{
    background-color: transparent;
    border: none;
    color: {theme['TEXT_DIM']};
    text-align: left;
    padding: 12px 15px;
    font-size: 11pt;
    font-weight: 500;
    border-left: 3px solid transparent;
    margin: 2px 0;
}}

QPushButton#NavButton:hover {{
    background-color: {theme['BG_HOVER']};
    color: {theme['TEXT_MAIN']};
}}

QPushButton#NavButton:checked {{
    background-color: {theme['BG_SELECTED']};
    color: {theme['TEXT_MAIN']};
    border-left: 3px solid {theme['ACCENT']};
}}

QLabel#NavCategory {{
    color: {theme['TEXT_DISABLED']};
    font-size: 8pt;
    font-weight: bold;
    text-transform: uppercase;
    padding: 15px 15px 5px 15px;
    letter-spacing: 0.5px;
}}

QFrame#NavSeparator {{
    background-color: {theme['BORDER']};
    border: none;
    max-height: 1px;
    margin: 5px 15px 5px 15px;
}}

/* Generic Buttons */
QPushButton {{
    background-color: {theme['BG_CARD']};
    border: 1px solid {theme['BORDER']};
    border-radius: 4px;
    color: {theme['TEXT_MAIN']};
    padding: 6px 12px;
}}

QPushButton:hover {{
    background-color: {theme['BG_HOVER']};
    border-color: {theme['TEXT_DIM']};
}}

QPushButton:pressed {{
    background-color: {theme['ACCENT']};
    border-color: {theme['ACCENT']};
    color: white;
}}

QPushButton:disabled {{
    background-color: {theme['BG_MAIN']};
    color: {theme['TEXT_DISABLED']};
    border-color: {theme['BORDER']};
}}

/* Primary Action Button */
QPushButton#PrimaryButton {{
    background-color: {theme['ACCENT']};
    border: 1px solid {theme['ACCENT']};
    color: white;
    font-weight: 600;
}}

QPushButton#PrimaryButton:hover {{
    background-color: {theme['ACCENT_HOVER']};
    border-color: {theme['ACCENT_HOVER']};
}}

QPushButton#PrimaryButton:pressed {{
    background-color: {theme['ACCENT_PRESSED']};
    border-color: {theme['ACCENT_PRESSED']};
}}

/* Input Fields */
QLineEdit, QSpinBox, QDoubleSpinBox, QComboBox {{
    background-color: {theme['BG_INPUT']};
    border: 1px solid {theme['BORDER']};
    border-radius: 4px;
    color: {theme['TEXT_MAIN']};
    padding: 5px;
    selection-background-color: {theme['ACCENT']};
}}

QLineEdit:focus, QSpinBox:focus, QDoubleSpinBox:focus, QComboBox:focus {{
    border: 1px solid {theme['BORDER_FOCUS']};
}}

/* Combo Box */
QComboBox::drop-down {{
    subcontrol-origin: padding;
    subcontrol-position: top right;
    width: 20px;
    border-left-width: 0px;
    border-top-right-radius: 4px;
    border-bottom-right-radius: 4px;
}}

QComboBox QAbstractItemView {{
    background-color: {theme['BG_CARD']};
    border: 1px solid {theme['BORDER']};
    selection-background-color: {theme['ACCENT']};
    selection-color: white;
    outline: none;
}}

/* List Widget */
QListWidget {{
    background-color: {theme['BG_INPUT']};
    border: 1px solid {theme['BORDER']};
    border-radius: 4px;
    outline: none;
}}

QListWidget::item {{
    padding: 5px;
    border-radius: 3px;
}}

QListWidget::item:selected {{
    background-color: {theme['ACCENT']};
    color: white;
}}

QListWidget::item:hover:!selected {{
    background-color: {theme['BG_HOVER']};
}}

/* Scrollbars */
QScrollBar:vertical {{
    border: none;
    background: {theme['BG_MAIN']};
    width: 10px;
    margin: 0px 0px 0px 0px;
}}

QScrollBar::handle:vertical {{
    background: #424242;
    min-height: 20px;
    border-radius: 5px;
    margin: 2px;
}}

QScrollBar::handle:vertical:hover {{
    background: #686868;
}}

QScrollBar::add-line:vertical, QScrollBar::sub-line:vertical {{
    height: 0px;
}}

QScrollBar:horizontal {{
    border: none;
    background: {theme['BG_MAIN']};
    height: 10px;
    margin: 0px 0px 0px 0px;
}}

QScrollBar::handle:horizontal {{
    background: #424242;
    min-width: 20px;
    border-radius: 5px;
    margin: 2px;
}}

QScrollBar::handle:horizontal:hover {{
    background: #686868;
}}

QScrollBar::add-line:horizontal, QScrollBar::sub-line:horizontal {{
    width: 0px;
}}

/* Group Box */
QGroupBox {{
    border: 1px solid {theme['BORDER']};
    border-radius: 6px;
    margin-top: 20px;
    font-weight: bold;
}}

QGroupBox::title {{
    subcontrol-origin: margin;
    subcontrol-position: top left;
    padding: 0 5px;
    left: 10px;
    color: {theme['TEXT_DIM']};
}}
"""

ARTEMIS_STYLESHEET = get_stylesheet("Dark")
