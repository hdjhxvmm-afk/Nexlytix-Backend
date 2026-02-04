# Nexlytix Backend

IoT telemetry ingestion service with MQTT and REST API.

## Quick Start
```bash
docker-compose up --build
```

## Architecture
```
app/
├── api/          # FastAPI routes
├── database/     # InfluxDB operations
├── mqtt/         # MQTT subscriber
└── security/     # Auth, rate limit, validation
```

## Services
| Service | Port | Description |
|---------|------|-------------|
| API | 8000 | REST API |
| MQTT | 1883 | Message broker |
| InfluxDB | 8086 | Time-series DB |

## Environment Variables
| Variable | Default | Description |
|----------|---------|-------------|
| API_KEY | dev-key | API authentication |
| HMAC_SECRET | dev-secret | Message signing |
| ALLOWED_ORIGINS | localhost:3000 | CORS origins |
| RATE_LIMIT | 100/minute | Rate limiting |

## API Docs
See [docs/API.md](docs/API.md)
