from django.db import models
from uuid import uuid4


class Payment(models.Model):
    PAYMENT_METHOD = (
        ("paypal", "Paypal"),
        ("stripe", "Stripe"),
        ("credit_card", "Credit Card"),
        ("debit_card", "Debit Card"),
    )
    PAYMENT_STATUS = (
        ("pending", "Pending"),
        ("paid", "Paid"),
        ("failed", "Failed"),
    )
    id = models.UUIDField(primary_key=True, default=uuid4, editable=False)
    user = models.ForeignKey("accounts.User", on_delete=models.CASCADE)
    membership = models.ForeignKey("memberships.Membership", on_delete=models.CASCADE)
    payment_date = models.DateField()
    method = models.CharField(
        max_length=11, choices=PAYMENT_METHOD, default="debit_card"
    )
    amount = models.DecimalField(
        max_digits=10, decimal_places=2, null=False, blank=False
    )
    status = models.CharField(max_length=10, choices=PAYMENT_STATUS, default="pending")
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.user.fullname} - {self.status}"
