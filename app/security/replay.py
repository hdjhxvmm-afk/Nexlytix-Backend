import logging

log = logging.getLogger(__name__)
_last_seq = {}

def check_replay(device_id: str, seq: int) -> bool:
    last = _last_seq.get(device_id, -1)
    if seq <= last:
        log.warning(f"Replay attack: {device_id} seq={seq} <= last={last}")
        return False
    _last_seq[device_id] = seq
    return True
