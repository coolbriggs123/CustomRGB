import random
import math

# --- NOISE FUNCTIONS ---

# Pre-compute permutation table for Perlin
PERLIN_PERM = list(range(256))
random.shuffle(PERLIN_PERM)
PERLIN_PERM += PERLIN_PERM
# Gradients for 1D: just -1 or 1 (or arbitrary floats)
PERLIN_GRADS = [random.uniform(-1, 1) for _ in range(256)]

def lerp(a, b, t):
    return a + (b - a) * t

def fade(t):
    return t * t * t * (t * (t * 6 - 15) + 10)

def perlin_1d(x):
    # Determine grid cell coordinates
    x0 = int(x) & 255
    x1 = (x0 + 1) & 255
    
    # Relative x within cell
    tx = x - int(x)
    
    # Compute fade curve
    u = fade(tx)
    
    # Hash coordinates of the 2 corners
    p = PERLIN_PERM
    a = p[x0]
    b = p[x1]
    
    # Gradient values
    ga = PERLIN_GRADS[a]
    gb = PERLIN_GRADS[b]
    
    # Blend
    # Dot product in 1D is just grad * dist
    val = lerp(ga * tx, gb * (tx - 1), u)
    
    # Normalize approx to 0..1 (usually output is -0.5 to 0.5 or so)
    # Perlin 1D theoretical range is [-0.5, 0.5] if grads are normalized
    return (val + 0.5)

def value_noise_1d(x, seed_table):
    idx = int(x) % 256
    next_idx = (idx + 1) % 256
    t = x - int(x)
    t = fade(t) # Use same smooth curve
    return lerp(seed_table[idx], seed_table[next_idx], t)

# --- BLENDING FUNCTIONS ---

def blend_color(base, active, mode, opacity):
    """
    base: (r, g, b) tuple 0-255 (Background)
    active: (r, g, b) tuple 0-255 (Foreground/Source)
    mode: str
    opacity: float 0.0-1.0
    Returns: (r, g, b)
    """
    if opacity <= 0: return base
    
    br, bg, bb = base
    ar, ag, ab = active
    
    # Convert to 0-1 for math
    br, bg, bb = br/255.0, bg/255.0, bb/255.0
    ar, ag, ab = ar/255.0, ag/255.0, ab/255.0
    
    out_r, out_g, out_b = br, bg, bb
    
    if mode == "Normal":
        out_r, out_g, out_b = ar, ag, ab
        
    elif mode == "Add":
        out_r = min(1.0, br + ar)
        out_g = min(1.0, bg + ag)
        out_b = min(1.0, bb + ab)
        
    elif mode == "Multiply":
        out_r = br * ar
        out_g = bg * ag
        out_b = bb * ab
        
    elif mode == "Screen":
        out_r = 1.0 - (1.0 - br) * (1.0 - ar)
        out_g = 1.0 - (1.0 - bg) * (1.0 - ag)
        out_b = 1.0 - (1.0 - bb) * (1.0 - ab)
        
    elif mode == "Overlay":
        def overlay_ch(b, a):
            if b < 0.5: return 2 * b * a
            else: return 1 - 2 * (1 - b) * (1 - a)
        out_r = overlay_ch(br, ar)
        out_g = overlay_ch(bg, ag)
        out_b = overlay_ch(bb, ab)
        
    elif mode == "Color Dodge":
        def dodge_ch(b, a):
            if a == 1.0: return 1.0
            val = b / (1.0 - a)
            return min(1.0, val)
        out_r = dodge_ch(br, ar)
        out_g = dodge_ch(bg, ag)
        out_b = dodge_ch(bb, ab)
        
    elif mode == "Subtract":
        out_r = max(0.0, br - ar)
        out_g = max(0.0, bg - ag)
        out_b = max(0.0, bb - ab)

    # Apply Opacity (Lerp between Base and Result)
    # Result = Base * (1-opacity) + Blended * opacity
    final_r = br * (1.0 - opacity) + out_r * opacity
    final_g = bg * (1.0 - opacity) + out_g * opacity
    final_b = bb * (1.0 - opacity) + out_b * opacity
    
    return (int(final_r * 255), int(final_g * 255), int(final_b * 255))
