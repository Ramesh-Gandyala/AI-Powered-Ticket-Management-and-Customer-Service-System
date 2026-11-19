
from rest_framework.permissions import BasePermission


class IsCustomerOrAdmin(BasePermission):

    message = "Only Customers and Admins can submit queries."

    def has_permission(self, request, view):

        user = request.user

        if not user or not user.is_authenticated:
            return False

        return user.role in ["CUSTOMER", "ADMIN"]



class IsAgentOrAdmin(BasePermission):

    message = "Only Agents and Admins can access this resource."

    def has_permission(self, request, view):

        user = request.user

        if not user or not user.is_authenticated:
            return False

        return user.role in ["AGENT", "ADMIN"]

class IsCustomer(BasePermission):

    message = "Only Customers can access this resource."

    def has_permission(self, request, view):

        user = request.user

        if not user or not user.is_authenticated:
            return False

        return user.role == "CUSTOMER"
