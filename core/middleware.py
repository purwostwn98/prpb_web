from django.conf import settings # type: ignore
from django.contrib.auth.views import redirect_to_login # type: ignore


class LoginRequiredMiddleware:
    """
    Require an authenticated session for every web page except the login page
    and paths that handle their own authentication (admin, JWT API, static).
    """
    PUBLIC_PATHS = ('/logout/',)
    PUBLIC_PREFIXES = ('/admin/', '/api/', settings.STATIC_URL)

    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        path = request.path
        is_public = (
            path == '/'
            or path in self.PUBLIC_PATHS
            or path.startswith(self.PUBLIC_PREFIXES)
        )
        if not is_public and not request.user.is_authenticated:
            return redirect_to_login(request.get_full_path())
        return self.get_response(request)
