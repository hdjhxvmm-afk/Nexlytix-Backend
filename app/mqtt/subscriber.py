import json, time, logging
from datetime import datetime
import paho.mqtt.client as mqtt
from app.config import settings
from app.database import write
from app.security import verify_hmac, check_replay, validate_device_id, validate_sensor_range

log = logging.getLogger(__name__)

def on_connect(client, userdata, flags, rc, props):
    if rc == 0:
        client.subscribe(settings.MQTT_TOPIC)
        log.info(f"subscribed: {settings.MQTT_TOPIC}")
    else:
        log.error(f"conn failed: {rc}")

def on_message(client, userdata, msg):
    try:
        raw = msg.payload
        d = json.loads(raw)
        
        device_id = d.get("device_id")
        sig = d.get("sig", "")
        seq = d.get("seq", 0)
        sensors = d.get("sensors", {})
        
        # Security: Validate device_id
        if not validate_device_id(device_id):
            log.warning(f"Invalid device_id rejected: {device_id}")
            return
        
        # Security: HMAC verification (skip if sig is empty for dev mode)
        if sig and not verify_hmac(raw, sig):
            log.warning(f"HMAC failed: {device_id}")
            return
        
        # Security: Replay protection
        if not check_replay(device_id, seq):
            return
        
        # Security: Sensor range validation
        temp = sensors.get("temp_c")
        hum = sensors.get("humidity_pct")
        vib = sensors.get("vibration_rms")
        if not validate_sensor_range(temp, hum, vib):
            log.warning(f"Sensor out of range: {device_id} | temp={temp} hum={hum} vib={vib}")
            return
        
        ts = datetime.fromisoformat(d.get("ts", "").replace("Z", "+00:00")) if d.get("ts") else datetime.utcnow()
        
        if write(device_id, ts, sensors, seq, d.get("status", "?")):
            log.info(f"{device_id} | seq={seq}")
            
    except json.JSONDecodeError as e:
        log.error(f"JSON error: {e}")
    except Exception as e:
        log.error(f"Processing error: {e}")

def on_disconnect(client, userdata, flags, rc, props):
    log.warning(f"disconnected: {rc}")

def run():
    c = mqtt.Client(mqtt.CallbackAPIVersion.VERSION2)
    c.on_connect = on_connect
    c.on_message = on_message
    c.on_disconnect = on_disconnect
    c.reconnect_delay_set(1, 30)
    while True:
        try:
            c.connect(settings.MQTT_BROKER, settings.MQTT_PORT, 60)
            c.loop_forever()
        except:
            time.sleep(5)
