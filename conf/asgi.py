from channels.routing import ProtocolTypeRouter, URLRouter
from channels.auth import AuthMiddlewareStack
from channels.security.websocket import AllowedHostsOriginValidator
from channels.sessions import SessionMiddlewareStack
from django.core.asgi import get_asgi_application
import os


os.environ.setdefault("DJANGO_SETTINGS_MODULE", "conf.settings")
django_asgi_application = get_asgi_application()

from apps.messenger.routing import websocket_urlpatterns

application = ProtocolTypeRouter(
    {
        "http": django_asgi_application,
        "websocket": AllowedHostsOriginValidator(
            SessionMiddlewareStack(
                AuthMiddlewareStack(
                    URLRouter(
                        websocket_urlpatterns,
                    ),
                ),
            ),
        ),
    },
)
