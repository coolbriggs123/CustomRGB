import soundcard as sc
import numpy as np
import threading
import time

class AudioDriver:
    def __init__(self, device_id):
        self.device_id = device_id
        self.active = False
        self.thread = None
        self.lock = threading.Lock()
        self.fft_data = np.zeros(513) # rfft of 1024 is 513 bins
        self.volume = 0.0
        self.ref_count = 0
        self.error_count = 0
        
    def start(self):
        if self.active:
            return
        self.active = True
        self.thread = threading.Thread(target=self._run, daemon=True)
        self.thread.start()
        
    def stop(self):
        self.active = False
        if self.thread:
            self.thread.join(timeout=0.5)
            self.thread = None
            
    def _run(self):
        try:
            # Use microphones with loopback to capture output
            all_mics = sc.all_microphones(include_loopback=True)
            mic = None
            
            # Find by ID
            for m in all_mics:
                if m.id == self.device_id:
                    mic = m
                    break
            
            if not mic:
                # Fallback to default microphone if available
                mic = sc.default_microphone()
                if not mic and all_mics:
                    mic = all_mics[0]
            
            if not mic:
                print(f"No audio device found for ID {self.device_id}")
                self.active = False
                return

            with mic.recorder(samplerate=44100) as recorder:
                while self.active:
                    try:
                        data = recorder.record(numframes=1024)
                        # data is (frames, channels)
                        if data.shape[1] > 1:
                            mono = np.mean(data, axis=1)
                        else:
                            mono = data.flatten()
                        
                        # Apply window function to reduce spectral leakage
                        window = np.hanning(len(mono))
                        mono_windowed = mono * window
                        
                        fft = np.fft.rfft(mono_windowed)
                        fft_mag = np.abs(fft)
                        
                        with self.lock:
                            self.fft_data = fft_mag
                            self.volume = np.max(np.abs(mono))
                        
                    except Exception as e:
                        # print(f"Audio loop error: {e}")
                        self.error_count += 1
                        time.sleep(0.1)
                        if self.error_count > 100:
                            print("Too many audio errors, stopping driver")
                            break
                        
        except Exception as e:
            print(f"Audio driver init error for {self.device_id}: {e}")
            self.active = False

    def get_data(self):
        with self.lock:
            # Return copy to avoid race conditions during read
            return self.fft_data.copy(), self.volume

class AudioManager:
    _drivers = {} # device_id -> AudioDriver
    _lock = threading.Lock()
    
    @classmethod
    def get_driver(cls, device_id):
        with cls._lock:
            if device_id not in cls._drivers:
                cls._drivers[device_id] = AudioDriver(device_id)
            
            driver = cls._drivers[device_id]
            driver.ref_count += 1
            if not driver.active:
                driver.start()
            return driver
        
    @classmethod
    def release_driver(cls, device_id):
        with cls._lock:
            if device_id in cls._drivers:
                driver = cls._drivers[device_id]
                driver.ref_count -= 1
                if driver.ref_count <= 0:
                    driver.stop()
                    del cls._drivers[device_id]

    @staticmethod
    def list_devices():
        try:
            # key: name, value: id
            devices = {}
            # List all capture devices including loopback
            for m in sc.all_microphones(include_loopback=True):
                name = m.name
                if name in devices:
                    name = f"{m.name} ({m.id})"
                devices[name] = m.id
            return devices
        except Exception as e:
            print(f"Error listing devices: {e}")
            return {"Default": "default"}
