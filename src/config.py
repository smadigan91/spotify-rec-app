import os
import redis

redis_connection = None

BASE_URL = os.environ.get('BASE_URL', 'http://localhost:8080')


SPOTIFY_CLIENT_ID = os.environ.get('SPOTIFY_CLIENT_ID')
if not SPOTIFY_CLIENT_ID:
    raise RuntimeError("Required environment variable SPOTIFY_CLIENT_ID is not defined")

SPOTIFY_CLIENT_SECRET = os.environ.get('SPOTIFY_CLIENT_SECRET')
if not SPOTIFY_CLIENT_SECRET:
    raise RuntimeError("Required environment variable SPOTIFY_CLIENT_SECRET is not defined")

REDIS_HOST = os.environ.get('REDIS_HOST')
if not REDIS_HOST:
    raise RuntimeError("Required environment variable REDIS_HOST is not defined")

REDIS_PORT = os.environ.get('REDIS_PORT')
if not REDIS_PORT:
    raise RuntimeError("Required environment variable REDIS_PORT is not defined")

SESSION_KEY = os.environ.get('SESSION_KEY')
if not SESSION_KEY:
    raise RuntimeError("Required environment variable SESSION_KEY is not defined")


def get_redis_connection():
    global redis_connection
    if redis_connection is None:
        redis_connection = redis.StrictRedis(host=REDIS_HOST, port=REDIS_PORT, retry_on_timeout=True,
                                             socket_timeout=10, socket_connect_timeout=1)
    return redis_connection
