from app.background.celery_worker import celery_app

from app.services.price_prediction import predict_service
import asyncio

