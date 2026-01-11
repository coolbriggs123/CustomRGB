import time

def blend(a, b, alpha):
    return (
        int(a[0]*(1-alpha) + b[0]*alpha),
        int(a[1]*(1-alpha) + b[1]*alpha),
        int(a[2]*(1-alpha) + b[2]*alpha)
    )

def render_loop(leds, effects, backend, global_settings=None, fps=60):
    if global_settings is None:
        global_settings = {'brightness': 1.0, 'identify_device': -1, 'fps_limit': fps}

    start = time.perf_counter()
    while True:
        # Dynamic FPS limit
        current_fps = global_settings.get('fps_limit', fps)
        if current_fps < 1: current_fps = 1
        
        frame_start = time.perf_counter()
        t = frame_start - start
        
        # Base frame
        frame = [(0,0,0)] * len(leds)

        # Render effects
        for effect in effects:
            if not effect.enabled:
                continue
            ef = effect.render(leds, t)
            frame = [blend(frame[i], ef[i], effect.opacity) for i in range(len(frame))]

        # Apply Identify Override
        # If identify_device is set to a device index, we flash that device white
        identify_idx = global_settings.get('identify_device', -1)
        if identify_idx != -1:
            # Flash at 4Hz
            flash = (int(t * 8) % 2) == 0
            for i, led_data in enumerate(leds):
                if isinstance(led_data, dict) and led_data['device_index'] == identify_idx:
                    frame[i] = (255, 255, 255) if flash else (0, 0, 0)

        # Apply global brightness
        brightness = global_settings.get('brightness', 1.0)
        if brightness != 1.0:
            frame = [(int(r*brightness), int(g*brightness), int(b*brightness)) for r,g,b in frame]

        backend.push_frame(frame)
        
        # Calculate sleep time to maintain target FPS
        elapsed = time.perf_counter() - frame_start
        sleep_time = max(0, (1.0 / current_fps) - elapsed)
        time.sleep(sleep_time)
