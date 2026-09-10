import re

from django.conf import settings
from django.contrib.auth.views import redirect_to_login


class LoginRequiredMiddleware:
    """Require an authenticated session for every page by default.

    Pages that must stay public (login, registration, the customer-facing
    service request form, etc.) are listed in settings.LOGIN_EXEMPT_URLS as
    regex patterns matched against the request path with the leading slash
    stripped. Add new public pages there instead of scattering
    @login_required exemptions across views.py.
    """

    def __init__(self, get_response):
        self.get_response = get_response
        self.exempt_urls = [
            re.compile(pattern) for pattern in getattr(settings, "LOGIN_EXEMPT_URLS", [])
        ]

    def __call__(self, request):
        if not request.user.is_authenticated:
            path = request.path_info.lstrip("/")
            if not any(pattern.match(path) for pattern in self.exempt_urls):
                return redirect_to_login(request.get_full_path())
        return self.get_response(request)
