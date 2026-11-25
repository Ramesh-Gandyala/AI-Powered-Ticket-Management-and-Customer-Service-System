from rest_framework.permissions import BasePermission


class IsAdminOrReadOnly(BasePermission):

    message = "Only Admins can create, update, or delete FAQs."

    def has_permission(self, request, view):

        user = request.user

        if not user or not user.is_authenticated:
            return False

        if user.role == "ADMIN":
            return True

        return request.method in ["GET", "HEAD", "OPTIONS"]