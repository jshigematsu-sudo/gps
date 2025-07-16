from django.urls import re_path
from current_meet_locations.consumers import ChatConsumer
from current_meet_locations.mobileConsumers import MobileConsumer

websocket_urlpatterns = [
    # チャット用 WebSocket
    re_path(
        r'^ws/current_meet_locations/(?P<membersNameParameter>[0-9a-f\-]+)/$',
        ChatConsumer.as_asgi()
    ),

    # モバイル用 WebSocket（エンドポイントを変える）
    re_path(
        r'^ws/current_meet_locations_mobile/(?P<siteUuid>[0-9a-f\-]+)/$',
        MobileConsumer.as_asgi()
    ),
]