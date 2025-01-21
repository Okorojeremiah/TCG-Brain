import redis


redis_client = redis.StrictRedis(host='localhost', port=6379, db=0)

def get_from_cache(key):
    value = redis_client.get(key)
    return None if value is None else eval(value)

def set_in_cache(key, value):
    redis_client.set(key, str(value), ex=3600)