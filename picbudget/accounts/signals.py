# accounts/signals.py
from django.db.models.signals import post_save
from django.dispatch import receiver
from .models import User
from picbudget.wallets.models import Wallet


@receiver(post_save, sender=User)
def create_wallet_for_user(sender, instance, created, **kwargs):
    """
    Creates a wallet for a new user when the user is created.
    This does not create a wallet for admin or superuser.
    """
    if created and not instance.is_admin:
        Wallet.objects.create(user=instance)
