import logging
from influxdb_client import InfluxDBClient
from influxdb_client.client.write_api import SYNCHRONOUS
from app.config import settings

log = logging.getLogger(__name__)
_client = None
_write_api = None
_query_api = None

def get_client():
    global _client, _write_api, _query_api
    if not _client:
        _client = InfluxDBClient(url=settings.INFLUXDB_URL, token=settings.INFLUXDB_TOKEN, org=settings.INFLUXDB_ORG)
        _write_api = _client.write_api(write_options=SYNCHRONOUS)
        _query_api = _client.query_api()
        log.info(f"InfluxDB connected: {settings.INFLUXDB_URL}")
    return _client, _write_api, _query_api
