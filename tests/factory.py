import random
from datetime import datetime, timezone, timedelta

DEVICES = [
    "VemCore-01",
    "VemCore-02",
    "SiteB-Gateway",
    "FactoryFloor-03",
    "Warehouse-Alpha",
]

# mostly ok, rarely not
_STATUSES = ["ok"] * 17 + ["warn"] * 2 + ["error"]


class TelemetryFactory:
    def __init__(self, device_id=None):
        self.device_id = device_id or random.choice(DEVICES)
        self._seq = random.randint(100, 999)

    def build(self, ts=None):
        self._seq += 1
        return {
            "device_id": self.device_id,
            "ts": (ts or datetime.now(timezone.utc)).isoformat(),
            "sensors": {
                "temp_c":        round(random.uniform(-5.0, 60.0), 2),
                "humidity_pct":  round(random.uniform(20.0, 90.0), 2),
                "vibration_rms": round(random.uniform(0.001, 2.0), 4),
            },
            "seq":    self._seq,
            "status": random.choice(_STATUSES),
            "sig":    "",
        }

    def build_many(self, n=10, hours=24):
        now  = datetime.now(timezone.utc)
        step = timedelta(hours=hours) / n
        return [self.build(ts=now - step * i) for i in range(n)]

    @staticmethod
    def all_devices(n=20):
        out = []
        for d in DEVICES:
            out += TelemetryFactory(device_id=d).build_many(n)
        return out
