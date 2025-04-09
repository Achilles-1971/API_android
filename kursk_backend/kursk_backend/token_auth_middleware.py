from urllib.parse import parse_qs
from channels.db import database_sync_to_async

class TokenAuthMiddleware:
    def __init__(self, inner):
        self.inner = inner

    async def __call__(self, scope, receive, send):
        return await TokenAuthMiddlewareInstance(scope, self.inner)(receive, send)


class TokenAuthMiddlewareInstance:
    def __init__(self, scope, inner):
        self.scope = dict(scope)
        self.inner = inner

    async def __call__(self, receive, send):
        from django.contrib.auth.models import AnonymousUser
        from rest_framework.authtoken.models import Token

        query_string = self.scope.get("query_string", b"").decode()
        headers = dict((k.decode(), v.decode()) for k, v in self.scope.get("headers", []))
        token_key = None

        # 1. Пытаемся достать из заголовка
        auth_header = headers.get("authorization")
        if auth_header and auth_header.startswith("Token "):
            token_key = auth_header.split(" ", 1)[1]

        # 2. Если нет — ищем в query string
        if not token_key:
            query_params = parse_qs(query_string)
            token_values = query_params.get("token")
            if token_values:
                token_key = token_values[0]

        # 3. Ищем пользователя по токену
        if token_key:
            try:
                token = await self.get_token(token_key)
                user = await database_sync_to_async(lambda: token.user)()
                self.scope["user"] = user
            except Token.DoesNotExist:
                self.scope["user"] = AnonymousUser()
        else:
            self.scope["user"] = AnonymousUser()

        # Передаём scope, receive и send напрямую в URLRouter
        return await self.inner(self.scope, receive, send)

    @staticmethod
    async def get_token(token_key):
        from rest_framework.authtoken.models import Token
        return await database_sync_to_async(Token.objects.get)(key=token_key)