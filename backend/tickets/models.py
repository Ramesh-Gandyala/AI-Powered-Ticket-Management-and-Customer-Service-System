
from django.conf import settings
from django.db import models


class Query(models.Model):

    class QueryStatus(models.TextChoices):
        PENDING = "PENDING", "Pending"
        TICKET_CREATED = "TICKET_CREATED", "Ticket Created"

    class QueryCategory(models.TextChoices):
        TECHNICAL = "TECH", "Technical Issues"
        BILLING = "BILL", "Billing Issues"
        ACCOUNT = "ACC", "Account Issues"
        GENERAL = "GEN", "General Enquiries"

    submitted_by = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name="submitted_queries"
    )

    query = models.TextField()

    category = models.CharField(
        max_length=10,
        choices=QueryCategory.choices,
        default=QueryCategory.GENERAL
    )

    status = models.CharField(
        max_length=20,
        choices=QueryStatus.choices,
        default=QueryStatus.PENDING
    )

    created_at = models.DateTimeField(auto_now_add=True)

    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"Query #{self.id} - {self.status}"



class Ticket(models.Model):

    class TicketStatus(models.TextChoices):
        OPEN = "OPEN", "Open"
        IN_PROGRESS = "IN_PROGRESS", "In Progress"
        CLOSED = "CLOSED", "Closed"

    ticket_id = models.CharField(
        max_length=30,
        unique=True
    )

    query = models.OneToOneField(
        "tickets.Query",
        on_delete=models.CASCADE,
        related_name="ticket"
    )

    customer = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="customer_tickets"
    )

    assigned_agent = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="assigned_tickets"
    )

    created_by = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.PROTECT,
        related_name="created_tickets"
    )

    status = models.CharField(
        max_length=20,
        choices=TicketStatus.choices,
        default=TicketStatus.OPEN
    )

    created_at = models.DateTimeField(auto_now_add=True)

    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return self.ticket_id


class TicketProgress(models.Model):

    ticket = models.ForeignKey(
        "tickets.Ticket",
        on_delete=models.CASCADE,
        related_name="progress_history"
    )

    previous_status = models.CharField(
        max_length=20,
        choices=Ticket.TicketStatus.choices,
        null=True,
        blank=True
    )

    new_status = models.CharField(
        max_length=20,
        choices=Ticket.TicketStatus.choices
    )

    updated_by = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.PROTECT,
        related_name="ticket_status_updates"
    )

    remarks = models.TextField(
        blank=True
    )

    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return (
            f"{self.ticket.ticket_id}: "
            f"{self.previous_status} -> {self.new_status}"
        )

class TicketSequence(models.Model):

    category = models.CharField(
        max_length=10,
        choices=Query.QueryCategory.choices,
        unique=True
    )

    last_number = models.PositiveIntegerField(
        default=0
    )

    def __str__(self):
        return f"{self.category} - {self.last_number}"

