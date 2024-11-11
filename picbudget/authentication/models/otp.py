from django.db import models
from django.utils import timezone
import random


class OTP(models.Model):
    user = models.OneToOneField("accounts.User", on_delete=models.CASCADE)
    otp = models.CharField(max_length=6, blank=True, null=True)
    expired_at = models.DateTimeField(null=True, blank=True)

    def __str__(self) -> str:
        return f"OTP for {self.user.full_name}"

    def generate_otp(self):
        self.otp = "".join([str(random.randint(0, 9)) for _ in range(6)])
        self.expired_at = timezone.now() + timezone.timedelta(minutes=5)
        self.save()
        return self.otp

    def validate_otp(self, otp_code):
        # Retrun True if otp_code is valid and not expired
        return self.otp == otp_code and self.expired_at > timezone.now()

    def get_user_email(self):
        return self.user.email
