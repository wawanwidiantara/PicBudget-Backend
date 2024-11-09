from django.db import models
from uuid import uuid4


# Create your models here.
class Transaction(models.Model):
    TRANSACTION_TYPE = [
        ("income", "Income"),
        ("expense", "Expense"),
        ("transfer", "Transfer"),
    ]
    id = models.UUIDField(primary_key=True, default=uuid4, editable=False)
    wallet = models.ForeignKey("wallets.Wallet", on_delete=models.CASCADE)
    type = models.CharField(max_length=10, choices=TRANSACTION_TYPE, default="expense")
    amount = models.DecimalField(max_digits=10, decimal_places=2)
    transaction_date = models.DateTimeField()
    location = models.CharField(max_length=255, blank=True, null=True)
    labels = models.ManyToManyField(
        "labels.Label", blank=True, related_name="transactions_labels"
    )
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ["-created_at"]

    def __str__(self):
        return self.wallet.user.full_name
