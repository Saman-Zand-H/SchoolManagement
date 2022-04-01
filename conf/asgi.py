from channels.routing import ProtocolTypeRouter, URLRouter
from channels.auth import AuthMiddlewareStack
from channels.security.websocket import AllowedHostsOriginValidator
from channels.sessions import SessionMiddlewareStack

from apps.messenger.routing import websocket_urlpatterns


application = ProtocolTypeRouter(
    {
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
