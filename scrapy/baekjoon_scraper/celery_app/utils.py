from celery import current_app as current_celery_app
from celery_app.config import get_settings as celery_settings

settings = celery_settings()


def create_celery():
    celery_app = current_celery_app
    celery_app.config_from_object(settings, namespace="CELERY")
    celery_app.conf.update(accept_content=["json"])
    celery_app.conf.update(task_serializer="json")
    celery_app.conf.update(result_serializer="json")
    celery_app.conf.update(worker_prefetch_multiplier=2)
    celery_app.conf.update(broker_connection_retry_on_startup=True)

    return celery_app
