from django.urls import path

from .consumers import messenger_consumer


websocket_urlpatterns = [
    path("ws/messenger/<str:group_id>/", messenger_consumer),
]