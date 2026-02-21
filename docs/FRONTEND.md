# Nexlytix — Frontend API Reference

> Base URL: `http://localhost:8000`  
> Auth: كل request على `/api/*` محتاج header: `X-API-Key: <key>`

---

## Endpoints

### `GET /`
Health check — مفيش auth.

```json
{ "status": "ok" }
```

---

### `GET /api/telemetry/{device_id}`

جيب آخر 10 readings لجهاز معين (آخر 24 ساعة).

**Headers**
```
X-API-Key: nx-prod-key-2026
```

**Path param**
| param | type | rules |
|---|---|---|
| `device_id` | string | alphanumeric + `-_` فقط، max 64 char |

**Response 200**
```json
{
  "device_id": "VemCore-01",
  "count": 10,
  "data": [
    {
      "time":          "2026-02-21T00:00:00+00:00",
      "device_id":     "VemCore-01",
      "temp_c":        27.4,
      "humidity_pct":  45.2,
      "vibration_rms": 0.032,
      "seq":           1024,
      "status":        "ok"
    }
  ]
}
```

**Error responses**
| code | سبب |
|---|---|
| `400` | `device_id` فيه حروف غلط أو أطول من 64 |
| `401` | مفيش API key أو key غلط |
| `429` | Rate limit — أكتر من 100 request/min |
| `500` | server error |

---

## Data Model (شكل الـ Record)

```
Reading
├── time           string   ISO 8601 timestamp (UTC)
├── device_id      string   اسم الجهاز (tag — indexed)
├── temp_c         number   درجة الحرارة بالسيلسيوس  [-5 → 60]
├── humidity_pct   number   نسبة الرطوبة             [20 → 90]
├── vibration_rms  number   الاهتزاز RMS             [0.001 → 2.0]
├── seq            integer  رقم تسلسلي (replay guard)
└── status         string   "ok" | "warn" | "error"
```

---

## الأجهزة المتاحة (Seeded Devices)

| device_id | الوصف |
|---|---|
| `VemCore-01` | الوحدة الأساسية |
| `VemCore-02` | الوحدة الثانوية |
| `SiteB-Gateway` | Gateway الموقع B |
| `FactoryFloor-03` | حساس الأرضية |
| `Warehouse-Alpha` | مراقبة المستودع |

---

## العلاقة بين البيانات

```
Device (logical)
│
│  one device → many readings
│
└──► sensor_reading
         ├── _time       ← auto timestamp
         ├── device_id   ← FK (Tag)
         ├── temp_c
         ├── humidity_pct
         ├── vibration_rms
         ├── seq
         └── status
```

> **ملاحظة:** مفيش device registry — الجهاز بيتعرف فقط من `device_id` جوه كل reading.  
> لو عايز تجيب قائمة الأجهزة، هتجمعها من responses اللي بتيجي.

---

## مثال — JavaScript Fetch

```javascript
const API_KEY = "nx-prod-key-2026";
const BASE    = "http://localhost:8000";

async function getTelemetry(deviceId) {
  const res = await fetch(`${BASE}/api/telemetry/${deviceId}`, {
    headers: { "X-API-Key": API_KEY },
  });

  if (!res.ok) throw new Error(`${res.status}`);
  return res.json();
  // { device_id, count, data: [...] }
}
```

## مثال — Axios

```javascript
const { data } = await axios.get(`/api/telemetry/VemCore-01`, {
  baseURL: "http://localhost:8000",
  headers: { "X-API-Key": "nx-prod-key-2026" },
});
// data.data  ← array of readings
// data.count ← number of readings
```

---

## Status Values

| value | معناه | لون مقترح |
|---|---|---|
| `ok` | كل حاجة تمام | 🟢 green |
| `warn` | في مشكلة محتملة | 🟡 yellow |
| `error` | في مشكلة فعلية | 🔴 red |
