import logging
from datetime import datetime
from influxdb_client import Point, WritePrecision
from app.config import settings
from app.database.client import get_client

log = logging.getLogger(__name__)

def write(device_id: str, ts: datetime, sensors: dict, seq: int, status: str) -> bool:
    _, write_api, _ = get_client()
    try:
        p = Point("sensor_reading").tag("device_id", device_id)
        p = p.field("temp_c", float(sensors.get("temp_c", 0)))
        p = p.field("humidity_pct", float(sensors.get("humidity_pct", 0)))
        p = p.field("vibration_rms", float(sensors.get("vibration_rms", 0)))
        p = p.field("seq", int(seq)).field("status", status).time(ts, WritePrecision.S)
        write_api.write(bucket=settings.INFLUXDB_BUCKET, org=settings.INFLUXDB_ORG, record=p)
        return True
    except Exception as e:
        log.error(e)
        return False
