import sys, os, argparse
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

import requests
from tests.factory import DEVICES

BASE   = "http://localhost:8000"
APIKEY = "nx-prod-key-2026"

passed = 0
failed = 0


def check(label, ok, info=""):
    global passed, failed
    if ok:
        passed += 1
        print(f"  pass  {label}" + (f"  ({info})" if info else ""))
    else:
        failed += 1
        print(f"  FAIL  {label}" + (f"  ({info})" if info else ""))


def run(base, key):
    s = requests.Session()
    s.timeout = 8

    # ----- health -----
    r = s.get(f"{base}/")
    check("GET /", r.status_code == 200, f"status={r.status_code}")
    check("body.status == ok", r.json().get("status") == "ok")

    # ----- valid telemetry -----
    r = s.get(f"{base}/api/telemetry/VemCore-01", headers={"X-API-Key": key})
    check("GET /api/telemetry/VemCore-01", r.status_code == 200, f"status={r.status_code}")
    if r.ok:
        b = r.json()
        check("has device_id",       "device_id" in b)
        check("has data list",        isinstance(b.get("data"), list))
        check("has count",            "count" in b,  f"count={b.get('count')}")
        if b["data"]:
            rec = b["data"][0]
            for field in ("time", "temp_c", "humidity_pct", "vibration_rms", "seq", "status"):
                check(f"  data[0].{field}", field in rec)

    # ----- auth -----
    r = s.get(f"{base}/api/telemetry/VemCore-01")
    check("no key → 401", r.status_code == 401, f"status={r.status_code}")

    r = s.get(f"{base}/api/telemetry/VemCore-01", headers={"X-API-Key": "wrong"})
    check("bad key → 401", r.status_code == 401, f"status={r.status_code}")

    # ----- validation -----
    for bad in ["!!!BAD!!!", "has space", "a" * 65]:
        r = s.get(f"{base}/api/telemetry/{bad}", headers={"X-API-Key": key})
        check(f"bad id '{bad[:12]}' → 400", r.status_code == 400, f"status={r.status_code}")

    # ----- all devices -----
    for dev in DEVICES:
        r = s.get(f"{base}/api/telemetry/{dev}", headers={"X-API-Key": key})
        cnt = r.json().get("count", "?") if r.ok else "err"
        check(f"telemetry/{dev}", r.status_code == 200, f"count={cnt}")

    # ----- summary -----
    total = passed + failed
    print(f"\n{passed}/{total} passed" + (" ✓" if failed == 0 else f"  ({failed} failed)"))
    sys.exit(0 if failed == 0 else 1)


if __name__ == "__main__":
    ap = argparse.ArgumentParser()
    ap.add_argument("--url", default=BASE)
    ap.add_argument("--key", default=APIKEY)
    args = ap.parse_args()
    run(args.url, args.key)
