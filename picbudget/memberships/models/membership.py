from django.db import models
from uuid import uuid4


# Create your models here.
class Membership(models.Model):
    MEMBERSHIP_TYPE = (
        ("monthly", "Monthly"),
        ("yearly", "Yearly"),
    )
    MEMBERSHIP_STATUS = (
        ("active", "Active"),
        ("inactive", "Inactive"),
    )
    id = models.UUIDField(primary_key=True, default=uuid4, editable=False)
    user = models.ForeignKey("accounts.User", on_delete=models.CASCADE)
    start_date = models.DateField()
    end_date = models.DateField()
    type = models.CharField(max_length=10, choices=MEMBERSHIP_TYPE, default="monthly")
    status = models.CharField(
        max_length=10, choices=MEMBERSHIP_STATUS, default="inactive"
    )
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.user.fullname} - {self.status}"
