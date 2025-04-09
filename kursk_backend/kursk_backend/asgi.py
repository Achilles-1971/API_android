import os
import django

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'kursk_backend.settings')
django.setup()  # ✅ СНАЧАЛА setup()

from channels.routing import ProtocolTypeRouter, URLRouter
from django.core.asgi import get_asgi_application
from kursk_backend.token_auth_middleware import TokenAuthMiddleware
import api.routing  # ✅ ТЕПЕРЬ можно

application = ProtocolTypeRouter({
    "http": get_asgi_application(),
    "websocket": TokenAuthMiddleware(
        URLRouter(api.routing.websocket_urlpatterns)
    ),
})
