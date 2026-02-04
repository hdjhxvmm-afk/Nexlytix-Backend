import os

class Settings:
    MQTT_BROKER = os.getenv("MQTT_BROKER", "localhost")
    MQTT_PORT = int(os.getenv("MQTT_PORT", 1883))
    MQTT_TOPIC = "nexlytix/+/+/telemetry"
    INFLUXDB_URL = os.getenv("INFLUXDB_URL", "http://localhost:8086")
    INFLUXDB_TOKEN = os.getenv("INFLUXDB_TOKEN", "nexlytix-admin-token")
    INFLUXDB_ORG = os.getenv("INFLUXDB_ORG", "nexlytix")
    INFLUXDB_BUCKET = os.getenv("INFLUXDB_BUCKET", "telemetry")
    API_HOST = os.getenv("API_HOST", "0.0.0.0")
    API_PORT = int(os.getenv("API_PORT", 8000))
    
    # Security
    API_KEY = os.getenv("API_KEY", "dev-key-change-in-prod")
    HMAC_SECRET = os.getenv("HMAC_SECRET", "dev-secret-change-in-prod")
    ALLOWED_ORIGINS = os.getenv("ALLOWED_ORIGINS", "http://localhost:3000,http://localhost:5173").split(",")
    RATE_LIMIT = os.getenv("RATE_LIMIT", "100/minute")

settings = Settings()
