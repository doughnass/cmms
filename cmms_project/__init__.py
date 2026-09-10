try:
    from .celery import app as celery_app
except Exception:
    # Celery is optional in this environment. If it's not installed,
    # avoid failing imports so manage.py and other commands work.
    celery_app = None

# expose celery app (may be None if Celery is not available)
__all__ = ("celery_app",)
