from django.core.mail import send_mail
from django.conf import settings
from .models import Notification
from .tasks import send_email_task, send_push_notification_task


def notify_user(user, notif_type, message, entity_type=None, entity_id=None, title=None, body=None, data=None):


    # 📝 Создаём внутреннее уведомление
    Notification.objects.create(
        user=user,
        type=notif_type,
        message=message,
        entity_type=entity_type,
        entity_id=entity_id,
    )

    # 🧠 Объединяем data с обязательными полями
    final_data = data.copy() if data else {}
    final_data["receiver_id"] = str(user.id)
    if entity_id:
        final_data["entity_id"] = str(entity_id)
    if notif_type:
        final_data["type"] = notif_type

    # 🚀 Отправляем push
    if title and body:
        send_push_notification_task.delay(
            user_id=user.id,
            notif_type=notif_type,
            title=title,
            body=body,
            data=final_data
        )



def send_event_email(user, subject, body):
    """
    Асинхронная отправка email пользователю.
    """
    send_email_task.delay(
        subject=subject,
        body=body,
        recipient_email=user.email
    )
