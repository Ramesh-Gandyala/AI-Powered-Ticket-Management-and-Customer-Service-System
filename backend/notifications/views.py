
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from rest_framework.permissions import IsAuthenticated

from .models import Notification
from .serializers import NotificationSerializer


class NotificationListAPIView(APIView):

    permission_classes = [IsAuthenticated]

    def get(self, request):

        notifications = Notification.objects.filter(
            recipient=request.user
        )

        unread_only = request.query_params.get("unread")

        if unread_only == "true":
            notifications = notifications.filter(is_read=False)

        serializer = NotificationSerializer(
            notifications,
            many=True
        )

        return Response(
            {
                "success": True,
                "count": notifications.count(),
                "data": serializer.data
            },
            status=status.HTTP_200_OK
        )


class MarkNotificationReadAPIView(APIView):

    permission_classes = [IsAuthenticated]

    def patch(self, request, pk):

        try:
            notification = Notification.objects.get(
                pk=pk,
                recipient=request.user
            )

        except Notification.DoesNotExist:
            return Response(
                {
                    "success": False,
                    "message": "Notification not found."
                },
                status=status.HTTP_404_NOT_FOUND
            )

        notification.is_read = True
        notification.save(update_fields=["is_read"])

        return Response(
            {
                "success": True,
                "message": "Notification marked as read."
            },
            status=status.HTTP_200_OK
        )
