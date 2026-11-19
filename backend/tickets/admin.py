
from django.contrib import admin
from .models import (
    Query,
    Ticket,
    TicketProgress,
    TicketSequence,
)


@admin.register(Query)
class QueryAdmin(admin.ModelAdmin):
    list_display = (
        "id",
        "submitted_by",
        "status",
        "created_at",
    )

    list_filter = ("status", "created_at")

    search_fields = (
        "query",
        "submitted_by__username",
        "submitted_by__email",
    )

    readonly_fields = ("created_at", "updated_at")


@admin.register(Ticket)
class TicketAdmin(admin.ModelAdmin):
    list_display = (
        "ticket_id",
        "customer",
        "assigned_agent",
        "created_by",
        "status",
        "created_at",
    )

    list_filter = ("status", "created_at")

    search_fields = (
        "ticket_id",
        "customer__username",
        "assigned_agent__username",
    )

    readonly_fields = ("created_at", "updated_at")


@admin.register(TicketProgress)
class TicketProgressAdmin(admin.ModelAdmin):
    list_display = (
        "ticket",
        "previous_status",
        "new_status",
        "updated_by",
        "created_at",
    )

    list_filter = ("new_status", "created_at")

    search_fields = (
        "ticket__ticket_id",
        "updated_by__username",
        "remarks",
    )

    readonly_fields = ("created_at",)

@admin.register(TicketSequence)
class TicketSequenceAdmin(admin.ModelAdmin):

    list_display = (
        "category",
        "last_number",
    )

    search_fields = ("category",)