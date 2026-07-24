from celery import Celery

from app.core.config import get_settings

settings = get_settings()
celery_app = Celery("cryptosage", broker=settings.redis_url, backend=settings.redis_url)
celery_app.conf.update(
    task_serializer="json",
    result_serializer="json",
    accept_content=["json"],
    timezone="UTC",
    beat_schedule={
        "record-cache-statistics": {
            "task": "app.workers.tasks.record_cache_statistics",
            "schedule": 300.0,
        },
        "invalidate-market-cache": {
            "task": "app.workers.tasks.invalidate_market_cache",
            "schedule": 900.0,
        },
    },
)
celery_app.autodiscover_tasks(["app.workers"])
