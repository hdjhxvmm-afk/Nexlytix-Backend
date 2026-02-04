import re

def validate_device_id(device_id: str) -> bool:
    if not device_id or not re.match(r'^[a-zA-Z0-9\-_]+$', device_id):
        return False
    return len(device_id) <= 64

def validate_sensor_range(temp_c, humidity_pct, vibration_rms) -> bool:
    if temp_c is not None and not (-50 <= temp_c <= 100):
        return False
    if humidity_pct is not None and not (0 <= humidity_pct <= 100):
        return False
    if vibration_rms is not None and not (0 <= vibration_rms <= 10):
        return False
    return True
