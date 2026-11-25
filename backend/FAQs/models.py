
from django.db import models


class FAQ(models.Model):

    class Category(models.TextChoices):
        TECHNICAL = 'TECHNICAL', 'Technical'
        BILLING = 'BILLING', 'Billing'
        ACCOUNT = 'ACCOUNT', 'Account'
        GENERAL = 'GENERAL', 'General'

    question = models.CharField(max_length=255, unique=True)

    answer = models.TextField()

    category = models.CharField(
        max_length=20,
        choices=Category.choices,
        default=Category.GENERAL
    )

    is_published = models.BooleanField(default=False)

    created_at = models.DateTimeField(auto_now_add=True)

    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return self.question
