# Messenger. Sockets. Chat logic.
from django.urls import path, include
from myapp.consumers import ChatConsumer

websocket_urlpatterns = [
    path("" , ChatConsumer.as_asgi()) , 
] 