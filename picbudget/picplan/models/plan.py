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
    user = models.ForeignKey("accounts.User", on_delete=models.CASCADE)
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

        super().save(*args, **kwargs)

        if not self.wallets.exists():
            user_wallets = self.user.wallets.all()
            self.wallets.set(user_wallets)

        if not self.labels.exists():
            self.labels.set(Label.objects.all())
