"""Task helpers for CMMS.

This module is resilient when Celery is not installed in the environment:
it exports a `shared_task` decorator that is a no-op fallback and the task
function will execute synchronously.
"""

import logging

from django.conf import settings
from django.core.mail import send_mail

try:
    from celery import shared_task  # type: ignore

    _CELERY_AVAILABLE = True
except Exception:
    # Provide a no-op decorator so importing this module doesn't fail when
    # Celery isn't installed (useful for lightweight dev/test environments).
    _CELERY_AVAILABLE = False

    def shared_task(*a, **kw):
        # Support both usages:
        #   @shared_task
        #   def func(...):
        #       ...
        # and
        #   @shared_task()
        #   def func(...):
        #       ...
        if len(a) == 1 and callable(a[0]) and not kw:
            # used as @shared_task without parentheses
            return a[0]

        def _decorator(func):
            return func

        return _decorator


logger = logging.getLogger(__name__)


@shared_task
def send_assignment_email(to_email, subject, message):
    """Send a simple assignment email.

    If Celery is available this will be scheduled as a background task; if not,
    the function will be called synchronously. Errors are logged and not
    re-raised to avoid breaking calling code.
    """
    from_email = getattr(settings, "DEFAULT_FROM_EMAIL", "no-reply@localhost")
    try:
        send_mail(subject, message, from_email, [to_email], fail_silently=False)
    except Exception as exc:
        # Log the error for debugging. Do not re-raise so a background worker
        # or synchronous caller won't crash the request flow.
        logger.exception("Failed to send assignment email to %s: %s", to_email, exc)
        return False
    return True
