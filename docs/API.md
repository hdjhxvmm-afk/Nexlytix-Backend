# Nexlytix Telemetry API

## Base URL
```
http://your-server:8000
```

## Authentication
All `/api/*` endpoints require an API key in the header:
```
X-API-Key: your-api-key
```

---

## Endpoints

### Health Check
```
GET /
```
**Response:**
```json
{"status": "ok"}
```

---

### Get Device Telemetry
```
GET /api/telemetry/{device_id}
```

**Headers:**
| Header | Value |
|--------|-------|
| X-API-Key | Your API key |

**Path Parameters:**
| Param | Type | Description |
|-------|------|-------------|
| device_id | string | Alphanumeric, max 64 chars |

**Success Response (200):**
```json
{
  "device_id": "VemCore-01",
  "count": 10,
  "data": [
    {
      "time": "2026-02-04T09:00:00+00:00",
      "device_id": "VemCore-01",
      "temp_c": 27.4,
      "humidity_pct": 45.2,
      "vibration_rms": 0.032,
      "seq": 1024,
      "status": "ok"
    }
  ]
}
```

**Error Responses:**
| Code | Description |
|------|-------------|
| 400 | Invalid device_id format |
| 401 | Missing or invalid API key |
| 429 | Rate limit exceeded |
| 500 | Internal server error |

---

## Rate Limiting
- 100 requests per minute per IP
- Returns `429 Too Many Requests` when exceeded

---

## Example (JavaScript)
```javascript
const response = await fetch('http://localhost:8000/api/telemetry/VemCore-01', {
  headers: {
    'X-API-Key': 'your-api-key'
  }
});
const data = await response.json();
```

## Example (Python)
```python
import requests

r = requests.get(
    'http://localhost:8000/api/telemetry/VemCore-01',
    headers={'X-API-Key': 'your-api-key'}
)
data = r.json()
```
