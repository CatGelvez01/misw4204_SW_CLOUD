"""
Celery application configuration.
"""

from celery import Celery
from kombu import Exchange, Queue
from app.core.config import settings

# Create Celery app
celery_app = Celery(
    "anb_rising_stars",
    broker=settings.celery_broker_url,
    backend=settings.celery_result_backend,
)

# Import tasks to register them
from app.tasks import video_tasks  # noqa: F401, E402

# Define exchanges and queues
default_exchange = Exchange("celery", type="direct")
dlq_exchange = Exchange("celery_dlq", type="direct")

# Configure Celery
celery_app.conf.update(
    task_serializer="json",
    accept_content=["json"],
    result_serializer="json",
    timezone="UTC",
    enable_utc=True,
    task_track_started=True,
    task_time_limit=30 * 60,  # 30 minutes
    task_soft_time_limit=25 * 60,  # 25 minutes
    worker_prefetch_multiplier=1,
    worker_max_tasks_per_child=1000,
    task_acks_late=True,
    worker_reject_on_worker_lost=True,
    # Dead Letter Queue configuration
    task_queues=(
        Queue(
            "celery",
            exchange=default_exchange,
            routing_key="celery",
            queue_arguments={
                "x-dead-letter-exchange": "celery_dlq",
                "x-dead-letter-routing-key": "failed",
            },
        ),
        Queue(
            "failed",
            exchange=dlq_exchange,
            routing_key="failed",
        ),
    ),
    task_default_queue="celery",
    task_default_exchange="celery",
    task_default_routing_key="celery",
)
