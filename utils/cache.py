from time import time

_cache = {}  # {query: (timestamp, (channel_id, msg_id))}

TTL = 60 * 5  # 5 min

def get_cache(q):
    v = _cache.get(q)
    if not v:
        return None
    ts, data = v
    if time() - ts > TTL:
        _cache.pop(q, None)
        return None
    return data

def set_cache(q, data):
    _cache[q] = (time(), data)
