import logging, threading
import uvicorn
from app.config import settings
from app.api.routes import app
from app.mqtt.subscriber import run as mqtt_run

logging.basicConfig(level=logging.INFO, format="%(asctime)s | %(levelname)s | %(message)s")

if __name__ == "__main__":
    threading.Thread(target=mqtt_run, daemon=True).start()
    uvicorn.run(app, host=settings.API_HOST, port=settings.API_PORT)
