from .engine import Layer
import math
import random
import colorsys
import numpy as np
from .utils import blend_color, perlin_1d, value_noise_1d
from .audio_driver import AudioManager

# --- GENERATORS ---

class SolidColorLayer(Layer):
    def __init__(self):
        super().__init__("Solid Color")
        self.params = {
            'color': (255, 0, 0),
            'blend_mode': ('Normal', ['Normal', 'Add', 'Multiply', 'Screen', 'Overlay', 'Color Dodge', 'Subtract']),
            'opacity': 1.0
        }
        
    def process(self, buffer, ctx):
        r, g, b = self.params['color']
        
        b_mode = self.params['blend_mode']
        if isinstance(b_mode, tuple): b_mode = b_mode[0]
        
        opacity = self.params['opacity']
        
        out = []
        for i in range(ctx['count']):
            base = buffer[i]
            blended = blend_color(base, (r, g, b), b_mode, opacity)
            out.append(blended)
        return out
    
    def from_dict(self, data):
        params = dict(data.get('params', {}))
        if 'color' not in params:
            r = params.get('r')
            g = params.get('g')
            b = params.get('b')
            if r is not None and g is not None and b is not None:
                params['color'] = (r, g, b)
        for k in ('r', 'g', 'b'):
            if k in params:
                params.pop(k)
        data = dict(data)
        data['params'] = params
        super().from_dict(data)

class GradientLayer(Layer):
    def __init__(self):
        super().__init__("Gradient")
        self.params = {
            'color_start': (255, 0, 0),
            'color_end': (0, 0, 255),
            'offset': 0.0,
            'scale': 1.0,
            'type': ('Linear', ['Linear', 'Mirror']),
            'blend_mode': ('Normal', ['Normal', 'Add', 'Multiply', 'Screen', 'Overlay', 'Color Dodge', 'Subtract']),
            'opacity': 1.0
        }

    def process(self, buffer, ctx):
        count = ctx['count']
        t = ctx['t']
        
        c1 = self.params['color_start']
        c2 = self.params['color_end']
        offset = self.params['offset']
        scale = self.params['scale']
        g_type = self.params['type']
        if isinstance(g_type, tuple): g_type = g_type[0]
        
        b_mode = self.params['blend_mode']
        if isinstance(b_mode, tuple): b_mode = b_mode[0]
        opacity = self.params['opacity']
        
        out = []
        for i in range(count):
            pos = (i / max(1, count)) * scale + offset
            
            if g_type == 'Mirror':
                pos = abs((pos % 2.0) - 1.0)
            else:
                pos = pos % 1.0
                
            r = int(c1[0] * (1-pos) + c2[0] * pos)
            g = int(c1[1] * (1-pos) + c2[1] * pos)
            b = int(c1[2] * (1-pos) + c2[2] * pos)
            
            base = buffer[i]
            blended = blend_color(base, (r, g, b), b_mode, opacity)
            out.append(blended)
        return out

class StrobeLayer(Layer):
    def __init__(self):
        super().__init__("Strobe")
        self.params = {
            'color': (255, 255, 255),
            'frequency': 5.0,
            'duty_cycle': 0.5,
            'blend_mode': ('Normal', ['Normal', 'Add', 'Multiply', 'Screen', 'Overlay', 'Color Dodge', 'Subtract']),
            'opacity': 1.0
        }

    def process(self, buffer, ctx):
        t = ctx['t']
        count = ctx['count']
        
        freq = self.params['frequency']
        duty = self.params['duty_cycle']
        color = self.params['color']
        
        b_mode = self.params['blend_mode']
        if isinstance(b_mode, tuple): b_mode = b_mode[0]
        opacity = self.params['opacity']
        
        # Calculate strobe state
        cycle = (t * freq) % 1.0
        is_on = cycle < duty
        
        out = []
        if not is_on:
            return buffer # Pass through if off
            
        for i in range(count):
            base = buffer[i]
            blended = blend_color(base, color, b_mode, opacity)
            out.append(blended)
        return out

class WaveLayer(Layer):
    def __init__(self):
        super().__init__("Wave Generator")
        self.params = {
            'speed': 1.0, 
            'freq': 1.0, 
            'type': ('sine', ['sine', 'triangle', 'saw', 'square']), 
            'color': (0, 255, 0),
            'direction': ('Forward', ['Forward', 'Backward']),
            'offset': 0.0,
            'width': 0.5, # For square wave
            'blend_mode': ('Normal', ['Normal', 'Add', 'Multiply', 'Screen', 'Overlay', 'Color Dodge', 'Subtract']),
            'opacity': 1.0
        }
        
    def process(self, buffer, ctx):
        t = ctx['t']
        count = ctx['count']
        speed = self.params['speed']
        freq = self.params['freq']
        offset_val = self.params.get('offset', 0.0)
        width = self.params.get('width', 0.5)
        
        wave_type = self.params['type']
        if isinstance(wave_type, tuple): wave_type = wave_type[0]
        
        direction = self.params['direction']
        if isinstance(direction, tuple): direction = direction[0]
        
        b_mode = self.params['blend_mode']
        if isinstance(b_mode, tuple): b_mode = b_mode[0]
        
        opacity = self.params['opacity']
        
        r, g, b = self.params['color']
        
        dir_mult = 1 if direction == 'Forward' else -1
        
        out = []
        for i in range(count):
            pos = i / max(1, count)
            phase = (t * speed * dir_mult) + (pos * freq) + offset_val
            
            val = 0.0
            if wave_type == 'sine':
                val = (math.sin(phase * 2 * math.pi) + 1) / 2
            elif wave_type == 'saw':
                val = phase % 1.0
            elif wave_type == 'triangle':
                val = abs((phase % 1.0) * 2 - 1)
            elif wave_type == 'square':
                val = 1.0 if (phase % 1.0) < width else 0.0
            
            nr, ng, nb = int(r*val), int(g*val), int(b*val)
            
            base = buffer[i]
            blended = blend_color(base, (nr, ng, nb), b_mode, opacity)
            out.append(blended)
        return out

class NoiseLayer(Layer):
    def __init__(self):
        super().__init__("Noise Generator")
        self.params = {
            'scale': 0.1, 
            'speed': 0.5, 
            'octaves': 1,
            'persistence': 0.5,
            'color': (0, 0, 255),
            'noise_type': ('Perlin', ['Perlin', 'Value', 'Ping Pong']),
            'blend_mode': ('Normal', ['Normal', 'Add', 'Multiply', 'Screen', 'Overlay', 'Color Dodge', 'Subtract']),
            'opacity': 1.0
        }
        self.seed = [random.random() for _ in range(256)]
        
    def process(self, buffer, ctx):
        t = ctx['t']
        count = ctx['count']
        scale = self.params['scale']
        speed = self.params['speed']
        octaves = int(self.params.get('octaves', 1))
        persistence = self.params.get('persistence', 0.5)
        
        r, g, b = self.params['color']
        
        n_type = self.params['noise_type']
        if isinstance(n_type, tuple): n_type = n_type[0]
        
        b_mode = self.params['blend_mode']
        if isinstance(b_mode, tuple): b_mode = b_mode[0]
        
        opacity = self.params['opacity']
        
        out = []
        base_offset = t * speed * 10
        
        for i in range(count):
            val = 0.0
            x = i * scale + base_offset
            
            if octaves > 1:
                # Fractal noise
                total = 0
                amplitude = 1.0
                max_val = 0.0
                freq = 1.0
                
                for _ in range(octaves):
                    curr_x = x * freq
                    sample = 0.0
                    if n_type == 'Perlin':
                        sample = perlin_1d(curr_x)
                    elif n_type == 'Value':
                        sample = value_noise_1d(curr_x, self.seed)
                    elif n_type == 'Ping Pong':
                        raw = perlin_1d(curr_x)
                        sample = 1.0 - abs(2.0 * raw - 1.0)
                        
                    total += sample * amplitude
                    max_val += amplitude
                    amplitude *= persistence
                    freq *= 2.0
                
                val = total / max_val if max_val > 0 else 0
                
            else:
                # Single octave
                if n_type == 'Perlin':
                    val = perlin_1d(x)
                elif n_type == 'Value':
                    val = value_noise_1d(x, self.seed)
                elif n_type == 'Ping Pong':
                    raw = perlin_1d(x)
                    val = 1.0 - abs(2.0 * raw - 1.0)
                
            val = max(0.0, min(1.0, val))
            
            nr, ng, nb = int(r*val), int(g*val), int(b*val)
            
            base_color = buffer[i]
            blended = blend_color(base_color, (nr, ng, nb), b_mode, opacity)
            out.append(blended)
            
        return out

class BreathingLayer(Layer):
    def __init__(self):
        super().__init__("Breathing")
        self.params = {
            'color': (255, 0, 0),
            'speed': 1.0,
            'min_brightness': 0.0,
            'max_brightness': 1.0,
            'blend_mode': ('Normal', ['Normal', 'Add', 'Multiply', 'Screen', 'Overlay', 'Color Dodge', 'Subtract']),
            'opacity': 1.0
        }

    def process(self, buffer, ctx):
        t = ctx['t']
        count = ctx['count']
        
        color = self.params['color']
        speed = self.params['speed']
        min_b = self.params['min_brightness']
        max_b = self.params['max_brightness']
        
        b_mode = self.params['blend_mode']
        if isinstance(b_mode, tuple): b_mode = b_mode[0]
        opacity = self.params['opacity']
        
        # Calculate brightness
        val = (math.sin(t * speed * 2 * math.pi) + 1) / 2 # 0 to 1
        brightness = min_b + val * (max_b - min_b)
        
        r, g, b = int(color[0] * brightness), int(color[1] * brightness), int(color[2] * brightness)
        
        out = []
        for i in range(count):
            base = buffer[i]
            blended = blend_color(base, (r, g, b), b_mode, opacity)
            out.append(blended)
        return out

class CheckerboardLayer(Layer):
    def __init__(self):
        super().__init__("Checkerboard")
        self.params = {
            'color_1': (255, 255, 255),
            'color_2': (0, 0, 0),
            'size': 5,
            'speed': 0.0,
            'blend_mode': ('Normal', ['Normal', 'Add', 'Multiply', 'Screen', 'Overlay', 'Color Dodge', 'Subtract']),
            'opacity': 1.0
        }

    def process(self, buffer, ctx):
        t = ctx['t']
        count = ctx['count']
        
        c1 = self.params['color_1']
        c2 = self.params['color_2']
        size = int(max(1, self.params['size']))
        speed = self.params['speed']
        
        b_mode = self.params['blend_mode']
        if isinstance(b_mode, tuple): b_mode = b_mode[0]
        opacity = self.params['opacity']
        
        offset = t * speed * 10
        
        out = []
        for i in range(count):
            # Check pattern
            pos = i + int(offset)
            is_c1 = (pos // size) % 2 == 0
            
            color = c1 if is_c1 else c2
            
            base = buffer[i]
            blended = blend_color(base, color, b_mode, opacity)
            out.append(blended)
        return out

class AudioVisualizerLayer(Layer):
    def __init__(self):
        super().__init__("Audio Visualizer")
        
        # Get devices
        self.devices = AudioManager.list_devices()
        self.device_names = list(self.devices.keys())
        default_device = self.device_names[0] if self.device_names else "Default"
        
        self.params = {
            'device': (default_device, self.device_names),
            'mode': ('Spectrum', ['Spectrum', 'Volume', 'Bass Pulse', 'Rainbow Spectrum']),
            'sensitivity': 1.0,
            'smoothing': 0.5,
            'threshold': 0.0,
            'speed': 1.0,
            'color_low': (0, 0, 255),
            'color_high': (255, 0, 0),
            'blend_mode': ('Normal', ['Normal', 'Add', 'Multiply', 'Screen', 'Overlay', 'Color Dodge', 'Subtract']),
            'opacity': 1.0
        }
        
        self.current_driver = None
        self.last_device_name = None
        self.prev_vals = None
        
    def _update_driver(self):
        device_name = self.params['device']
        if isinstance(device_name, tuple): device_name = device_name[0]
        
        if device_name != self.last_device_name:
            # Release old
            if self.last_device_name and self.last_device_name in self.devices:
                old_id = self.devices[self.last_device_name]
                AudioManager.release_driver(old_id)
            
            # Acquire new
            if device_name in self.devices:
                new_id = self.devices[device_name]
                self.current_driver = AudioManager.get_driver(new_id)
            else:
                self.current_driver = None
                
            self.last_device_name = device_name

    def process(self, buffer, ctx):
        self._update_driver() # Check if device changed
        
        if not self.current_driver:
            return buffer
            
        fft_data, volume = self.current_driver.get_data()
        count = ctx['count']
        t = ctx['t']
        
        mode = self.params['mode']
        if isinstance(mode, tuple): mode = mode[0]
        
        sensitivity = self.params['sensitivity']
        smoothing = self.params.get('smoothing', 0.5)
        threshold = self.params.get('threshold', 0.0)
        speed = self.params['speed']
        
        b_mode = self.params['blend_mode']
        if isinstance(b_mode, tuple): b_mode = b_mode[0]
        
        opacity = self.params['opacity']
        
        color_low = self.params['color_low']
        color_high = self.params['color_high']
        
        out = []
        target_vals = np.zeros(count)
        
        if mode == 'Spectrum':
            start_bin = 2
            end_bin = 100 
            relevant_fft = fft_data[start_bin:end_bin]
            
            if len(relevant_fft) > 0:
                indices = np.linspace(0, len(relevant_fft)-1, count)
                target_vals = np.interp(indices, np.arange(len(relevant_fft)), relevant_fft)
                
            target_vals = target_vals * sensitivity / 10.0

        elif mode == 'Volume':
            vol = volume * sensitivity * 5.0
            vol = max(0.0, min(1.0, vol))
            
            center = count / 2
            width = vol * count / 2
            
            # Generate volume shape
            for i in range(count):
                dist = abs(i - center)
                val = 1.0 if dist < width else 0.0
                if dist > width and dist < width + 1:
                    val = 1.0 - (dist - width)
                target_vals[i] = val
                
        elif mode == 'Bass Pulse':
            bass = np.mean(fft_data[2:10]) * sensitivity / 5.0
            bass = max(0.0, min(1.0, bass))
            target_vals[:] = bass

        elif mode == 'Rainbow Spectrum':
            start_bin = 2
            end_bin = 100 
            relevant_fft = fft_data[start_bin:end_bin]
            
            if len(relevant_fft) > 0:
                indices = np.linspace(0, len(relevant_fft)-1, count)
                target_vals = np.interp(indices, np.arange(len(relevant_fft)), relevant_fft)
                
            target_vals = target_vals * sensitivity / 10.0
            
        # Apply smoothing
        if self.prev_vals is None or len(self.prev_vals) != count:
            self.prev_vals = np.zeros(count)
            
        # Smooth and clip
        self.prev_vals = self.prev_vals * smoothing + target_vals * (1.0 - smoothing)
        vals = np.clip(self.prev_vals, 0, 1)
        
        # Apply threshold
        vals = np.where(vals < threshold, 0, vals)
        # Rescale after threshold? Optional, but let's keep it simple for now (just cut off)
        if threshold < 1.0:
            vals = (vals - threshold) / (1.0 - threshold)
            vals = np.maximum(0, vals)

        # Render to buffer
        for i in range(count):
            val = vals[i]
            
            if mode == 'Rainbow Spectrum':
                hue = (i / count + t * speed * 0.1) % 1.0
                rgb = colorsys.hsv_to_rgb(hue, 1.0, 1.0)
                r, g, b = int(rgb[0]*255), int(rgb[1]*255), int(rgb[2]*255)
            else:
                # Interpolate color for non-rainbow modes
                # Or for volume/bass use high/low
                # The original code did different things for different modes.
                # Let's standardize: interpolate between low and high based on value
                r = int(color_low[0] * (1-val) + color_high[0] * val)
                g = int(color_low[1] * (1-val) + color_high[1] * val)
                b = int(color_low[2] * (1-val) + color_high[2] * val)

            # Apply brightness
            r = int(r * val)
            g = int(g * val)
            b = int(b * val)
            
            base = buffer[i]
            blended = blend_color(base, (r, g, b), b_mode, opacity)
            out.append(blended)
            
        return out

NODE_TYPES = {
    "Solid Color": SolidColorLayer,
    "Gradient": GradientLayer,
    "Checkerboard": CheckerboardLayer,
    "Breathing": BreathingLayer,
    "Strobe": StrobeLayer,
    "Wave Generator": WaveLayer,
    "Noise Generator": NoiseLayer,
    "Audio Visualizer": AudioVisualizerLayer
}

NODE_CATEGORIES = {
    "Generators": ["Solid Color", "Gradient", "Checkerboard"],
    "Animations": ["Breathing", "Strobe", "Wave Generator", "Noise Generator"],
    "Audio": ["Audio Visualizer"]
}

# Mapping for serialization (Class Name -> Class)
NODE_CLASSES = {cls.__name__: cls for cls in NODE_TYPES.values()}
