from config.config import Config


class BaseSettings:
    """Celery Configuration for Redis"""

    # Example Redis configuration, replace with your actual Redis URL and port
    broker_url = Config.CELERY_BROKER_URL
    result_backend = Config.CELERY_RESULT_BACKEND

    worker_concurrency = 10
    log_level = 'INFO'
    include: list = ['tasks']

    # Redis-specific configurations (if needed)
    broker_transport_options = {
        'visibility_timeout': 3600
    }


def get_settings():
    return BaseSettings()