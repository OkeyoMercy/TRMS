from channels.routing import ProtocolTypeRouter, URLRouter
from django.urls import path
from TMSapp import consumers

application = ProtocolTypeRouter({
    "websocket": URLRouter([
        path("ws/communicate/", consumers.DriverConsumer.asgi()),
    ]),
})