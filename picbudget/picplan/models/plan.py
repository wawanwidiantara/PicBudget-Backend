from django.db import models
from django.utils.timezone import now
from datetime import timedelta
from django.db.models import Sum
from picbudget.labels.models import Label
from picbudget.wallets.models import Wallet
from picbudget.transactions.models import Transaction
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
    notify_overspent = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def save(self, *args, **kwargs):

        super().save(*args, **kwargs)

        if not self.wallets.exists():
            user_wallets = Wallet.objects.filter(user=self.user)
            self.wallets.set(user_wallets)

        if not self.labels.exists():
            self.labels.set(Label.objects.all())

    def calculate_progress(self):
        now_date = now().date()
        start_date, end_date = None, None

        if self.period == "monthly":
            start_date = now_date.replace(day=1)
            end_date = start_date.replace(
                month=start_date.month + 1, day=1
            ) - timedelta(days=1)
        elif self.period == "weekly":
            start_date = now_date - timedelta(days=now_date.weekday())
            end_date = start_date + timedelta(days=6)
        elif self.period == "yearly":
            start_date = now_date.replace(month=1, day=1)
            end_date = now_date.replace(month=12, day=31)
        else:
            start_date, end_date = None, None

        transactions = Transaction.objects.filter(
            wallet__in=self.wallets.all(),
            labels__in=self.labels.all(),
        )
        if start_date and end_date:
            transactions = transactions.filter(
                transaction_date__range=(start_date, end_date)
            )

        total_spent = (
            transactions.aggregate(total_spent=Sum("amount"))["total_spent"] or 0
        )
        progress = (total_spent / self.amount) * 100 if self.amount > 0 else 0
        return round(progress, 2)

    def is_overspent(self):
        return self.calculate_progress() > 100

    def __str__(self):
        return self.name
