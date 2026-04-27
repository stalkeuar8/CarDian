from app.settings.config import redis_settings
from slowapi import Limiter
from fastapi.requests import Request
from slowapi.util import get_remote_address

def get_ip_and_path(request: Request):
    ip = request.client.host
    path = request.scope['path']
    return f"{ip}:{path}"


rate_limiter = Limiter(
    key_func=get_ip_and_path,
    storage_uri=redis_settings.REDIS_url
)
