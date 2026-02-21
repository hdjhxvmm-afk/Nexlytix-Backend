import sys, os, argparse
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from datetime import datetime, timezone
from influxdb_client import InfluxDBClient, Point, WritePrecision
from influxdb_client.client.write_api import SYNCHRONOUS

from tests.factory import TelemetryFactory, DEVICES
from app.config import settings


def _to_point(r):
    s = r["sensors"]
    return (
        Point("sensor_reading")
        .tag("device_id", r["device_id"])
        .field("temp_c",        float(s["temp_c"]))
        .field("humidity_pct",  float(s["humidity_pct"]))
        .field("vibration_rms", float(s["vibration_rms"]))
        .field("seq",           int(r["seq"]))
        .field("status",        r["status"])
        .time(datetime.fromisoformat(r["ts"]), WritePrecision.S)
    )


def seed(device_id, count):
    client   = InfluxDBClient(url=settings.INFLUXDB_URL, token=settings.INFLUXDB_TOKEN, org=settings.INFLUXDB_ORG)
    write_api = client.write_api(write_options=SYNCHRONOUS)

    devices = [device_id] if device_id else DEVICES
    total   = 0

    print(f"seeding {count} records × {len(devices)} devices → {settings.INFLUXDB_URL}")

    for dev in devices:
        records = TelemetryFactory(device_id=dev).build_many(n=count)
        write_api.write(
            bucket=settings.INFLUXDB_BUCKET,
            org=settings.INFLUXDB_ORG,
            record=[_to_point(r) for r in records],
        )
        total += count
        print(f"  {dev}: {count} records ok")

    print(f"\ndone. {total} total records written.")
    client.close()


if __name__ == "__main__":
    ap = argparse.ArgumentParser()
    ap.add_argument("--device", default=None)
    ap.add_argument("--count",  type=int, default=50)
    args = ap.parse_args()
    seed(args.device, args.count)
