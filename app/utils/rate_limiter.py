from app.settings.config import redis_settings
from slowapi import Limiter
from slowapi.util import get_remote_address


rate_limiter = Limiter(
    key_func=get_remote_address,
    storage_uri=redis_settings.REDIS_url
)
