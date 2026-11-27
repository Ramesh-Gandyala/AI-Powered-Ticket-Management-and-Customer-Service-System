
from .models import Notification
from django.conf import settings
from django.core.mail import send_mail


def create_notification(
    recipient,
    title,
    message,
    notification_type
):

    notification = Notification.objects.create(
        recipient=recipient,
        title=title,
        message=message,
        notification_type=notification_type
    )

    return notification


def send_notification_email(recipient, subject, message):

    if not recipient.email:
        return False

    email_count = send_mail(
        subject=subject,
        message=message,
        from_email=settings.DEFAULT_FROM_EMAIL,
        recipient_list=[recipient.email],
        fail_silently=False
    )

    return email_count == 1

