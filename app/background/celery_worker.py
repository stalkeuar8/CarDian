from celery import Celery
from app.settings.config import redis_settings

celery_app = Celery(
    "cardian_celery_worker", 
    broker=redis_settings.REDIS_url, 
    backend=redis_settings.REDIS_url, 
    include=[
        'app.background.lookups_processing_tasks', 
        'app.background.watchlists_tasks'
    ]
)

celery_app.autodiscover_tasks(['app.background.tasks'], force=True)