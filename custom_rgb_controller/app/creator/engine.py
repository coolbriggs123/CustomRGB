import time

class CreatorEffect():
    def __init__(self):
        self.enabled = True
        self.opacity = 1.0
        self.layers = [] # List of Layer instances
        self.active_keys = set()
    
    def add_layer(self, layer):
        self.layers.append(layer)
        
    def clear_layers(self):
        self.layers = []
        
    def handle_key_event(self, key, pressed):
        if pressed:
            self.active_keys.add(key)
        else:
            self.active_keys.discard(key)
            
    def render(self, leds, t):
        # Base buffer: Black
        buffer = [(0, 0, 0)] * len(leds)
        
        # Context for layers
        ctx = {
            't': t,
            'leds': leds,
            'keys': self.active_keys,
            'count': len(leds)
        }
        
        for layer in self.layers:
            if not layer.enabled: continue
            
            # Each layer processes the buffer
            # Some might be generators (overwrite), some modifiers (blend)
            buffer = layer.process(buffer, ctx)
            
        return buffer

    def to_dict(self):
        return {
            'layers': [layer.to_dict() for layer in self.layers]
        }

    def load_from_dict(self, data, node_types):
        self.clear_layers()
        for layer_data in data.get('layers', []):
            class_name = layer_data.get('class')
            layer_class = node_types.get(class_name)
            if layer_class:
                layer = layer_class()
                layer.from_dict(layer_data)
                self.add_layer(layer)

class Layer:
    def __init__(self, name="Layer"):
        self.name = name
        self.enabled = True
        self.params = {}
        
    def process(self, buffer, ctx):
        return buffer
        
    def set_param(self, key, value):
        self.params[key] = value
        
    def get_param(self, key, default=None):
        return self.params.get(key, default)

    def to_dict(self):
        # Convert params to serializable format if needed
        # For now assume params are simple types (int, float, str, tuple)
        # JSON handles lists, but tuples become lists. We might need to handle that on load.
        return {
            'class': self.__class__.__name__,
            'name': self.name,
            'enabled': self.enabled,
            'params': self.params
        }

    def from_dict(self, data):
        self.name = data.get('name', self.name)
        self.enabled = data.get('enabled', True)
        
        # Restore params with type correction for tuples vs lists
        if 'params' in data:
            new_params = data['params']
            for k, v in new_params.items():
                if k not in self.params:
                    continue
                default_val = self.params[k]
                if isinstance(default_val, tuple) and isinstance(v, list):
                    v = tuple(v)
                self.params[k] = v
