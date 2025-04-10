import firebase_admin
from firebase_admin import credentials, messaging
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from rest_framework.permissions import IsAuthenticated
from rest_framework.serializers import Serializer, CharField
import logging

logger = logging.getLogger(__name__)

# Инициализация Firebase (один раз)
if not firebase_admin._apps:
    import json
    from django.conf import settings
    from decouple import config
    firebase_credentials = config('FIREBASE_CREDENTIALS')
    cred = credentials.Certificate(json.loads(firebase_credentials))
    firebase_admin.initialize_app(cred)


def send_push_notification(token: str, title: str, body: str, data: dict = None):
    from firebase_admin import messaging
    message = messaging.Message(
        notification=messaging.Notification(
            title=title,
            body=body,
        ),
        token=token,
        data=data or {}
    )
    try:
        response = messaging.send(message)
        logger.info(f"✅ Успешно отправлено: {response}")
        return response
    except Exception as e:
        logger.error(f"❌ Ошибка при отправке: {e}")
        return None


def send_push_if_allowed(user, notif_type: str, title: str, body: str, data: dict = None):
    from api.models import FCMToken
    category_map = {
        'event_joined': 'events',
        'event_left': 'events',
        'event_comment': 'events',
        'event_comment_reply': 'events',
        'event_submitted': 'moderation',
        'event_approved': 'moderation',
        'event_rejected': 'moderation',
        'comment_liked': 'likes_comments',
        'event_reminder': 'events',
        'new_message': 'messages',
    }

    category = category_map.get(notif_type)
    if not category:
        logger.warning(f"⚠️ Тип уведомления '{notif_type}' не сопоставлен с категорией.")
        return

    settings = getattr(user, 'push_settings', None)
    if settings is None or not getattr(settings, category, False):
        logger.info(f"🔕 Push отключён для категории '{category}' у пользователя {user.username}")
        return

    token_obj = FCMToken.objects.filter(user=user).last()
    if not token_obj:
        logger.warning(f"⚠️ У пользователя {user.username} нет FCM-токена.")
        return

    try:
        response = send_push_notification(token_obj.token, title, body, data)
        logger.info(f"✅ Уведомление отправлено пользователю {user.username}: {response}")
        return response
    except Exception as e:
        logger.error(f"❌ Ошибка при отправке push-уведомления пользователю {user.username}: {e}")
        return None


class FcmTokenSerializer(Serializer):
    token = CharField(max_length=255)


class RegisterFcmTokenView(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request):
        from api.models import FCMToken
        serializer = FcmTokenSerializer(data=request.data)
        if not serializer.is_valid():
            logger.warning(f"⚠️ Неверные данные для FCM-токена: {serializer.errors}")
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

        token = serializer.validated_data['token']
        user = request.user

        try:
            fcm_token, created = FCMToken.objects.get_or_create(token=token)
            if not created:
                if fcm_token.user != user:
                    old_user = fcm_token.user
                    fcm_token.user = user
                    fcm_token.save()
                    logger.info(f"ℹ️ Токен {token} перепривязан от {old_user.username if old_user else 'никого'} к {user.username}")
                    return Response({"message": "Token reassigned to current user"}, status=status.HTTP_200_OK)
                logger.info(f"ℹ️ Токен {token} уже зарегистрирован для {user.username}")
                return Response({"message": "Token already registered for this user"}, status=status.HTTP_200_OK)
            fcm_token.user = user
            fcm_token.save()
            logger.info(f"✅ Токен {token} зарегистрирован для {user.username}")
            return Response({"message": "Token registered successfully"}, status=status.HTTP_201_CREATED)
        except Exception as e:
            logger.error(f"❌ Ошибка при регистрации токена {token} для {user.username}: {e}")
            return Response({"error": str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)