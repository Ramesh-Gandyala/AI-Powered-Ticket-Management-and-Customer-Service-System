
from django.urls import path

from .views import (
    QuerySubmissionAPIView,
    PendingQueriesAPIView,
    AllQueriesAPIView,
    MyQueriesAPIView,
    TicketCreationAPIView,
    AllTicketsAPIView,
    MyTicketsAPIView,
    TicketStatusUpdateAPIView,
    MyTicketProgressAPIView,
)


urlpatterns = [
    path(
        "raise-query/",
        QuerySubmissionAPIView.as_view(),
        name="raise-query",
    ),

    path(
        "pending-queries/",
        PendingQueriesAPIView.as_view(),
        name="pending-queries",
    ),

    path(
        "all-queries/",
        AllQueriesAPIView.as_view(),
        name="all-queries",
    ),

    path(
        "my-queries/",
        MyQueriesAPIView.as_view(),
        name="my-queries",
    ),

    path(
        "create-ticket/",
        TicketCreationAPIView.as_view(),
        name="create-ticket",
    ),

    path(
        "all-tickets/",
        AllTicketsAPIView.as_view(),
        name="all-tickets",
    ),

    path(
        "my-tickets/",
        MyTicketsAPIView.as_view(),
        name="my-tickets",
    ),

    path(
        "tickets/<str:ticket_id>/update-status/",
        TicketStatusUpdateAPIView.as_view(),
        name="update-ticket-status",
    ),

    path(
        "my-tickets/<str:ticket_id>/progress/",
        MyTicketProgressAPIView.as_view(),
        name="my-ticket-progress",
    ),

]
