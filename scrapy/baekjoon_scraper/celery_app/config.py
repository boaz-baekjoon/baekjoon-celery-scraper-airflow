from config.config import Config


class BaseSettings:
    """Celery Configuration for Redis"""

    # Example Redis configuration, replace with your actual Redis URL and port
    broker_url = Config.celery_broker_url
    result_backend = Config.celery_result_backend

    worker_concurrency = 4
    log_level = 'INFO'
    include: list = ['tasks']

    # Redis-specific configurations (if needed)
    broker_transport_options = {
        'visibility_timeout': 3600
    }


def get_settings():
    return BaseSettings()