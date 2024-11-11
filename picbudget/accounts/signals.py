# accounts/signals.py
from django.db.models.signals import post_save
from django.dispatch import receiver
from .models import User
from picbudget.wallets.models import Wallet
from picbudget.authentication.serializers.otp import OTPSerializer


@receiver(post_save, sender=User)
def create_wallet_for_user(sender, instance, created, **kwargs):
    """
    Creates a wallet for a new user when the user is created.
    This does not create a wallet for admin or superuser.
    """
    if created and not instance.is_admin:
        Wallet.objects.create(user=instance)


# create OTP for user
@receiver(post_save, sender=User)
def create_otp_for_user(sender, instance, created, **kwargs):
    """
    Creates an OTP for a new user when the user is created.
    This does not create an OTP for admin or superuser.
    """
    if created and not instance.is_admin:
        serializer = OTPSerializer(data={"email": instance.email})
        serializer.is_valid(raise_exception=True)
        serializer.save()
