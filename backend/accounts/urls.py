
from django.urls import path

from .views import (
    AdminEmailVerificationAPIView,
    AdminLoginAPIView,
    AgentLoginAPIView,
    AgentEmailVerificationAPIView,
    AgentRegistrationAPIView,
    CustomerEmailVerificationAPIView,
    CustomerRegistrationAPIView,
    CustomerLoginAPIView,
)


urlpatterns = [
    path(
        "admin/verify-email/<int:uid>/<str:token>/",
        AdminEmailVerificationAPIView.as_view(),
        name="admin-email-verification"
    ),

    path(
        "agent/verify-email/<int:uid>/<str:token>/",
        AgentEmailVerificationAPIView.as_view(),
        name="agent-email-verification"
    ),

    path(
        "admin/login/",
        AdminLoginAPIView.as_view(),
        name="admin-login"
    ),

    path(
        "agent/login/",
        AgentLoginAPIView.as_view(),
        name="agent-login"
    ),

    path(
        "agent/register/",
        AgentRegistrationAPIView.as_view(),
        name="agent-registration"
    ),

    path(
        "customer/verify-email/<int:uid>/<str:token>/",
        CustomerEmailVerificationAPIView.as_view(),
        name="customer-email-verification"
    ),

    path(
        "customer/register/",
        CustomerRegistrationAPIView.as_view(),
        name="customer-registration"
    ),

    path(
        "customer/login/",
        CustomerLoginAPIView.as_view(),
        name="customer-login"
    ),
]
