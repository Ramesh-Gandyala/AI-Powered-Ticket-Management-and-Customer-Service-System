from django.db import transaction

from .models import TicketSequence


@transaction.atomic
def generate_ticket_id(category):

    sequence, created = TicketSequence.objects.get_or_create(
        category=category,
        defaults={"last_number": 0}
    )

    sequence = TicketSequence.objects.select_for_update().get(
        pk=sequence.pk
    )

    sequence.last_number += 1
    sequence.save(update_fields=["last_number"])

    ticket_number = str(sequence.last_number).zfill(4)

    return f"TMS-{category}-{ticket_number}"

