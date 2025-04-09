import json
import logging
from channels.generic.websocket import AsyncWebsocketConsumer
from channels.db import database_sync_to_async
from django.utils import timezone
from api.serializers import UserSerializer
from api.models import Message
from api.tasks import notify_message_receiver

logger = logging.getLogger(__name__)

class ChatConsumer(AsyncWebsocketConsumer):
    async def connect(self):
        self.user = self.scope['user']
        if not self.user.is_authenticated:
            await self.close()
            return

        # Подключаем пользователя ко всем группам его чатов
        await self.add_to_all_chat_groups()
        await self.accept()
        logger.info(f"WebSocket connected for user: {self.user.username} (ID: {self.user.id})")

    async def disconnect(self, close_code):
        # Отключаем пользователя от всех групп
        chat_groups = await self.get_user_chat_groups()
        for group in chat_groups:
            await self.channel_layer.group_discard(group, self.channel_name)
        logger.info(f"WebSocket disconnected for user: {self.user.username} (ID: {self.user.id})")

    async def receive(self, text_data):
        try:
            data = json.loads(text_data)
            content = data.get('content')
            to_user_id = data.get('to_user_id')
            if not content or not to_user_id:
                await self.send(text_data=json.dumps({'error': 'Content and to_user_id are required'}))
                return

            to_user = await self.get_user(to_user_id)
            if not to_user:
                await self.send(text_data=json.dumps({'error': 'User not found'}))
                return

            # Формируем группу чата
            ids = sorted([str(self.user.id), str(to_user_id)])
            room_group_name = f"chat_{ids[0]}_{ids[1]}"

            # Сохраняем сообщение
            message = await self.save_message(content, to_user)

            # Формируем данные для отправки
            message_data = {
                'id': message.id,
                'sender': UserSerializer(self.user).data,
                'receiver': to_user.id,
                'content': message.content,
                'timestamp': message.sent_at.isoformat(),
                'message_type': 'text',
                'read_at': message.read_at.isoformat() if message.read_at else None,
            }

            # Отправляем сообщение в группу
            await self.channel_layer.group_send(
                room_group_name,
                {
                    'type': 'chat_message',
                    'message_data': message_data,
                }
            )

            # Отправляем уведомление
            notify_message_receiver.delay(message.id)

        except Exception as e:
            logger.error(f"Error in receive: {e}")
            await self.send(text_data=json.dumps({'error': str(e)}))

    async def chat_message(self, event):
        await self.send(text_data=json.dumps({
            'message_data': event['message_data']
        }))

    @database_sync_to_async
    def save_message(self, content, to_user):
        return Message.objects.create(
            from_user=self.user,
            to_user=to_user,
            content=content,
            sent_at=timezone.now()
        )

    @database_sync_to_async
    def get_user(self, user_id):
        from api.models import User
        try:
            return User.objects.get(id=user_id)
        except User.DoesNotExist:
            return None

    @database_sync_to_async
    def get_user_chat_groups(self):
        from api.models import Message
        from django.db.models import Q
        messages = Message.objects.filter(Q(from_user=self.user) | Q(to_user=self.user)) \
            .values('from_user', 'to_user').distinct()
        groups = []
        for msg in messages:
            other_id = msg['to_user'] if msg['from_user'] == self.user.id else msg['from_user']
            ids = sorted([str(self.user.id), str(other_id)])
            groups.append(f"chat_{ids[0]}_{ids[1]}")
        return groups

    async def add_to_all_chat_groups(self):
        chat_groups = await self.get_user_chat_groups()
        for group in chat_groups:
            await self.channel_layer.group_add(group, self.channel_name)