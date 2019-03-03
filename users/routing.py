from django.urls import path

from . import consumers

websocket_urlpatterns = [
    path('ws/game/<uuid:game_id>/', consumers.GameConsumer)
]
