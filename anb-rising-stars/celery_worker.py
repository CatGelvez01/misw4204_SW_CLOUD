"""
Entry point for running Celery worker.
"""

from app.tasks.celery_app import celery_app
from app.tasks import video_tasks  # noqa: F401

if __name__ == "__main__":
    celery_app.worker_main(
        [
            "worker",
            "--loglevel=info",
            "--concurrency=4",
        ]
    )
