# Nexlytix — Frontend Integration Guide

> كل اللي محتاجه عشان تبدأ تشتغل مع الـ API

---

## Quick Start

**Base URL:** `http://localhost:8000`  
**API Key:** `nx-prod-key-2026`  
**الـ API read-only** — بتجيب بيانات بس، مفيش POST.

```js
// ابسط شكل ممكن
const res  = await fetch('http://localhost:8000/api/telemetry/VemCore-01', {
  headers: { 'X-API-Key': 'nx-prod-key-2026' }
})
const data = await res.json()
// data.device_id → "VemCore-01"
// data.count     → 10
// data.data      → [ { time, temp_c, humidity_pct, vibration_rms, seq, status } ]
```

---

## الـ Endpoints

| Method | URL | Auth | الوظيفة |
|---|---|---|---|
| `GET` | `/` | لأ | Health check |
| `GET` | `/api/telemetry/{device_id}` | نعم | آخر 10 readings للجهاز |

---

## شكل الـ Response

```ts
// GET /api/telemetry/{device_id}
type TelemetryResponse = {
  device_id : string
  count     : number
  data      : Reading[]
}

type Reading = {
  time          : string   // ISO 8601 e.g. "2026-02-21T01:00:00+00:00"
  device_id     : string
  temp_c        : number   // -5 → 60
  humidity_pct  : number   // 20 → 90
  vibration_rms : number   // 0.001 → 2.0
  seq           : number   // رقم تسلسلي
  status        : 'ok' | 'warn' | 'error'
}
```

---

## الأجهزة المتاحة

```ts
const DEVICES = [
  'VemCore-01',
  'VemCore-02',
  'SiteB-Gateway',
  'FactoryFloor-03',
  'Warehouse-Alpha',
]
```

لو عايز تجيب بيانات كل الأجهزة، اعمل request لكل واحد منفردًا.  
**مفيش endpoint يرجع كل الأجهزة دفعة واحدة** — ده قرار متعمد للـ rate limiting.

---

## الـ Status Colors

```ts
const statusColor = {
  ok    : '#22c55e',  // green
  warn  : '#f59e0b',  // amber
  error : '#ef4444',  // red
}
```

---

## Error Handling

| Status | السبب | التصرف |
|---|---|---|
| `400` | `device_id` فيه حروف غلط | تحقق من الـ input |
| `401` | API key غلط أو مش موجود | تحقق من الـ header |
| `429` | أكتر من 100 req/min | اعمل throttle أو cache |
| `500` | server error | retry بعد ثانيتين |

```ts
async function getTelemetry(deviceId: string) {
  const res = await fetch(`http://localhost:8000/api/telemetry/${deviceId}`, {
    headers: { 'X-API-Key': 'nx-prod-key-2026' }
  })

  if (res.status === 401) throw new Error('invalid api key')
  if (res.status === 429) throw new Error('rate limited')
  if (!res.ok)            throw new Error(`server error ${res.status}`)

  return res.json() as Promise<TelemetryResponse>
}
```

---

## Live Data (Polling)

الـ API مش WebSocket. عشان تعمل real-time dashboard، استخدم polling كل 5 ثواني:

```ts
// React example
useEffect(() => {
  const fetch = () => getTelemetry('VemCore-01').then(setData)
  fetch()
  const id = setInterval(fetch, 5000)
  return () => clearInterval(id)
}, [])
```

---

## مثال كامل — React Hook

```ts
// hooks/useTelemetry.ts
import { useState, useEffect } from 'react'

const BASE   = 'http://localhost:8000'
const APIKEY = 'nx-prod-key-2026'

export function useTelemetry(deviceId: string, intervalMs = 5000) {
  const [data,    setData]    = useState<TelemetryResponse | null>(null)
  const [loading, setLoading] = useState(true)
  const [error,   setError]   = useState<string | null>(null)

  useEffect(() => {
    let active = true

    const load = async () => {
      try {
        const res = await fetch(`${BASE}/api/telemetry/${deviceId}`, {
          headers: { 'X-API-Key': APIKEY }
        })
        if (!res.ok) throw new Error(res.status.toString())
        const json = await res.json()
        if (active) { setData(json); setError(null) }
      } catch (e: any) {
        if (active) setError(e.message)
      } finally {
        if (active) setLoading(false)
      }
    }

    load()
    const id = setInterval(load, intervalMs)
    return () => { active = false; clearInterval(id) }
  }, [deviceId, intervalMs])

  return { data, loading, error }
}
```

**استخدامه:**
```tsx
const { data, loading, error } = useTelemetry('VemCore-01')

if (loading) return <Spinner />
if (error)   return <Alert>{error}</Alert>

return (
  <div>
    <h2>{data.device_id}</h2>
    <p>Temp: {data.data[0]?.temp_c}°C</p>
    <p>Status: {data.data[0]?.status}</p>
  </div>
)
```

---

## مثال — Vue 3 Composable

```ts
// composables/useTelemetry.ts
import { ref, onMounted, onUnmounted } from 'vue'

export function useTelemetry(deviceId: string) {
  const data    = ref(null)
  const loading = ref(true)

  const load = async () => {
    const res  = await fetch(`http://localhost:8000/api/telemetry/${deviceId}`, {
      headers: { 'X-API-Key': 'nx-prod-key-2026' }
    })
    data.value    = await res.json()
    loading.value = false
  }

  let interval: ReturnType<typeof setInterval>
  onMounted(() => { load(); interval = setInterval(load, 5000) })
  onUnmounted(() => clearInterval(interval))

  return { data, loading }
}
```

---

## env Variables (مهم للـ Production)

```env
# .env
VITE_API_BASE=http://localhost:8000
VITE_API_KEY=nx-prod-key-2026
```

```ts
const BASE   = import.meta.env.VITE_API_BASE
const APIKEY = import.meta.env.VITE_API_KEY
```

> ⚠️ الـ API key في الـ frontend هيبقى visible للـ user. ده مقبول في بيئة الـ development. في الـ production، روحها عبر backend proxy.

---

## CORS

الـ server بيقبل requests من:
- `http://localhost:3000`
- `http://localhost:5173`

لو الـ port بتاعك مختلف، قول للـ backend developer يضيفه.
