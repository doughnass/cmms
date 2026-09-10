import os

os.environ.setdefault("DJANGO_SETTINGS_MODULE", "cmms_project.settings")

try:
    from celery import Celery

    app = Celery("cmms_project")
    app.config_from_object("django.conf:settings", namespace="CELERY")
    app.autodiscover_tasks()
except Exception:
    # Celery is not installed in this environment. Provide a lightweight
    # fallback so importing this module does not crash manage.py or tests.
    class _NoopApp:
        def task(self, *args, **kwargs):
            def _decorator(func):
                return func

            return _decorator

    app = _NoopApp()
