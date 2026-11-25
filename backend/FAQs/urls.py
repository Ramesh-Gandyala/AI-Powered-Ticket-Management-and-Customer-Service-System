from django.urls import path

from .views import (
    FAQListCreateAPIView,
    FAQDetailAPIView,
)

urlpatterns = [
    path(
        "",
        FAQListCreateAPIView.as_view(),
        name="faq-list-create",
    ),

    path(
        "<int:faq_id>/",
        FAQDetailAPIView.as_view(),
        name="faq-detail",
    ),
]