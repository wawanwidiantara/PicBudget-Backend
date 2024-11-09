from django.db import models
from uuid import uuid4


# Create your models here.
class Wallet(models.Model):
    WALLET_TYPE = (
        ("cash", "Cash"),
        ("bank", "Bank"),
        ("ewallet", "E-Wallet"),
    )
    id = models.UUIDField(primary_key=True, default=uuid4, editable=False)
    user = models.ForeignKey("accounts.User", on_delete=models.CASCADE)
    name = models.CharField(max_length=50, blank=False, null=False, default="My Wallet")
    type = models.CharField(max_length=10, choices=WALLET_TYPE, default="cash")
    balance = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def save(self, *args, **kwargs):
        if not self.pk:
            base_name = self.name
            counter = 1
            while Wallet.objects.filter(user=self.user, name=self.name).exists():
                counter += 1
                self.name = f"{base_name} {counter}"
        super().save(*args, **kwargs)

    def __str__(self):
        return f"{self.user.fullname} - {self.name}"
