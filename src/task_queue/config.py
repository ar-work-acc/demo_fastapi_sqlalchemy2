"""
1. Celery configuration class `Config`.
2. Custom task class with settings `BaseTask`;
   usage `@app.task(base=BaseTask)`;
   you can configure most options here instead of in every `@app.task`.
   # https://docs.celeryq.dev/en/stable/userguide/tasks.html#automatic-retry-for-known-exceptions
"""

from celery import Task
from kombu import Exchange, Queue

from core.config import PROJECT_SETTINGS


class Config:
    enable_utc = True
    timezone = "Asia/Taipei"
    broker_url = str(PROJECT_SETTINGS.CELERY_BROKER_URL)
    result_backend = str(PROJECT_SETTINGS.CELERY_BACKEND)

    # task queue settings
    default_exchange = Exchange("default", type="direct")
    task_queues = (
        Queue("default", default_exchange, routing_key="default"),
        # define other queues here
    )
    task_default_queue = "default"
    task_default_exchange_type = "direct"
    task_default_routing_key = "default"


class BaseTask(Task):  # pragma: no cover
    autoretry_for = (Exception,)
    dont_autoretry_for = (None,)
    default_retry_delay = 5 * 60
    max_retries = 1
    retry_backoff = True
    retry_backoff_max = 12 * 60
    retry_jitter = True  # default
