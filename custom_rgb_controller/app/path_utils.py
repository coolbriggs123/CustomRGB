import os
import sys

def get_app_root():
    """
    Returns the base path of the application.
    If frozen (exe), returns the directory containing the exe.
    Otherwise, returns the project root directory.
    """
    if getattr(sys, 'frozen', False):
        # Running as compiled exe
        return os.path.dirname(sys.executable)
    else:
        # Running from source
        # This file is in app/path_utils.py, so root is two levels up
        return os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

def get_asset_path(relative_path):
    """
    Get absolute path to resource, works for dev and for PyInstaller.
    Use this for read-only assets bundled with the app.
    """
    try:
        # PyInstaller creates a temp folder and stores path in _MEIPASS
        base_path = sys._MEIPASS
    except Exception:
        base_path = get_app_root()
    
    return os.path.join(base_path, relative_path)
