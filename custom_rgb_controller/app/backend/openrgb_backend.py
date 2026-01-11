import os
import shutil
import subprocess
import time

from openrgb import OpenRGBClient
from openrgb.utils import RGBColor

def _is_openrgb_server_ready(host: str, port: int) -> bool:
    try:
        client = OpenRGBClient(address=host, port=int(port))
        client.disconnect()
        return True
    except Exception:
        return False

def _find_openrgb_executable(explicit_path: str | None = None) -> str | None:
    if explicit_path:
        expanded = os.path.expandvars(os.path.expanduser(explicit_path))
        if os.path.isfile(expanded):
            return expanded

    for candidate in ("OpenRGB.exe", "OpenRGB"):
        found = shutil.which(candidate)
        if found:
            return found

    for candidate in (
        r"C:\Program Files\OpenRGB\OpenRGB.exe",
        r"C:\Program Files (x86)\OpenRGB\OpenRGB.exe",
    ):
        if os.path.isfile(candidate):
            return candidate

    return None

def start_openrgb_server(host: str, port: int, exe_path: str | None = None) -> subprocess.Popen | None:
    exe = _find_openrgb_executable(exe_path)
    if not exe:
        return None

    args = [
        exe,
        "--server",
        "--server-host",
        str(host),
        "--server-port",
        str(int(port)),
        "--gui",
        "--startminimized",
    ]

    creationflags = 0
    if os.name == "nt":
        creationflags = getattr(subprocess, "DETACHED_PROCESS", 0) | getattr(subprocess, "CREATE_NEW_PROCESS_GROUP", 0)

    return subprocess.Popen(
        args,
        stdout=subprocess.DEVNULL,
        stderr=subprocess.DEVNULL,
        stdin=subprocess.DEVNULL,
        creationflags=creationflags,
        close_fds=(os.name != "nt"),
    )

class OpenRGBBackend:
    def __init__(self, host: str = "127.0.0.1", port: int = 6742):
        self.client = OpenRGBClient(address=host, port=int(port))

    @staticmethod
    def is_installed() -> bool:
        return _find_openrgb_executable() is not None

    @staticmethod
    def is_server_running(host: str, port: int) -> bool:
        return _is_openrgb_server_ready(host, int(port))

    @staticmethod
    def ensure_server_running(host: str, port: int, exe_path: str | None = None, wait_s: float | None = None) -> subprocess.Popen | None:
        probe_host = host
        if probe_host in ("0.0.0.0", "::"):
            probe_host = "127.0.0.1"

        if _is_openrgb_server_ready(probe_host, int(port)):
            return None

        proc = start_openrgb_server(host, int(port), exe_path=exe_path)
        if wait_s is None:
            while not _is_openrgb_server_ready(probe_host, int(port)):
                time.sleep(0.2)
            return proc
        if not proc:
            return None

        deadline = time.time() + max(0.0, float(wait_s))
        while time.time() < deadline:
            if _is_openrgb_server_ready(probe_host, int(port)):
                break
            time.sleep(0.2)

        return proc

    def get_led_map(self):
        """
        Returns a list of metadata dicts for each LED in global order.
        """
        map_data = []
        global_index = 0
        for dev_idx, device in enumerate(self.client.devices):
            num_leds = len(device.leds)
            for local_index in range(num_leds):
                map_data.append({
                    'global_index': global_index,
                    'device_index': dev_idx,
                    'device_name': device.name,
                    'local_index': local_index,
                    'device_total': num_leds
                })
                global_index += 1
        return map_data

    def push_frame(self, frame):
        i = 0
        for device in self.client.devices:
            leds = device.leds
            colors = []
            for _ in leds:
                if i < len(frame):
                    r, g, b = frame[i]
                    colors.append(RGBColor(r, g, b))
                i += 1
            if colors:
                device.set_colors(colors)
