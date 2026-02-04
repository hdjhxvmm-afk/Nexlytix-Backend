from app.config import settings
from app.database.client import get_client

def query(device_id: str, limit: int = 10) -> list:
    _, _, query_api = get_client()
    q = f'''from(bucket: "{settings.INFLUXDB_BUCKET}")
      |> range(start: -24h)
      |> filter(fn: (r) => r["device_id"] == "{device_id}")
      |> pivot(rowKey:["_time"], columnKey: ["_field"], valueColumn: "_value")
      |> sort(columns: ["_time"], desc: true)
      |> limit(n: {limit})'''
    
    tables = query_api.query(q, org=settings.INFLUXDB_ORG)
    return [{"time": r.get_time().isoformat(), "device_id": r.values.get("device_id"),
             "temp_c": r.values.get("temp_c"), "humidity_pct": r.values.get("humidity_pct"),
             "vibration_rms": r.values.get("vibration_rms"), "seq": r.values.get("seq"),
             "status": r.values.get("status")} for t in tables for r in t.records]
