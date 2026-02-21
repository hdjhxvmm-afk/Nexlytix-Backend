import sys, os, json, time, argparse
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

import paho.mqtt.client as mqtt
from app.config import settings
from tests.factory import TelemetryFactory, DEVICES


def seed(device_id, count, delay):
    devices = [device_id] if device_id else DEVICES

    c = mqtt.Client(mqtt.CallbackAPIVersion.VERSION2)
    c.connect(settings.MQTT_BROKER, settings.MQTT_PORT, 60)
    c.loop_start()

    print(f"publishing to {settings.MQTT_BROKER}:{settings.MQTT_PORT}")

    total = 0
    for dev in devices:
        f     = TelemetryFactory(device_id=dev)
        topic = f"nexlytix/{settings.INFLUXDB_ORG}/{dev}/telemetry"
        for _ in range(count):
            msg = f.build()
            c.publish(topic, json.dumps(msg), qos=1).wait_for_publish()
            print(f"  [{dev}] seq={msg['seq']} temp={msg['sensors']['temp_c']}°C")
            total += 1
            time.sleep(delay)

    c.loop_stop()
    c.disconnect()
    print(f"\n{total} messages sent.")


if __name__ == "__main__":
    ap = argparse.ArgumentParser()
    ap.add_argument("--device", default=None)
    ap.add_argument("--count",  type=int,   default=10)
    ap.add_argument("--delay",  type=float, default=0.2)
    args = ap.parse_args()
    seed(args.device, args.count, args.delay)
