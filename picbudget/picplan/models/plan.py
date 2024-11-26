from django.db import models
from picbudget.labels.models import Label
from uuid import uuid4


class Plan(models.Model):
    PERIOD_TYPE = [
        ("one-time", "One-time"),
        ("weekly", "Weekly"),
        ("monthly", "Monthly"),
        ("yearly", "Yearly"),
    ]

    id = models.UUIDField(primary_key=True, default=uuid4, editable=False)
    name = models.CharField(max_length=100)
    amount = models.DecimalField(max_digits=10, decimal_places=2)
    period = models.CharField(max_length=10, choices=PERIOD_TYPE, default="monthly")
    labels = models.ManyToManyField(
        "labels.Label", blank=True, related_name="plans_labels"
    )
    wallets = models.ManyToManyField(
        "wallets.Wallet", blank=True, related_name="plans_wallets"
    )
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def save(self, *args, **kwargs):
        if not self.pk:
            user = kwargs.pop("user", None)
            if user:
                self.save_base(*args, **kwargs)
                self.labels.set(Label.objects.all())
                self.wallets.set(user.wallets.all())
        else:
            super().save(*args, **kwargs)
