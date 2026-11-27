
from django.urls import path

from .views import (
    NotificationListAPIView,
    MarkNotificationReadAPIView,
)


urlpatterns = [

    # View all notifications or unread notifications
    path(
        "notifications/",
        NotificationListAPIView.as_view(),
        name="notification-list"
    ),

    # Mark a notification as read
    path(
        "notifications/<int:pk>/read/",
        MarkNotificationReadAPIView.as_view(),
        name="notification-mark-read"
    ),

]
