from uuid import uuid4
from django.db import models
from django.contrib.auth.models import AbstractBaseUser
from ..managers.account import UserManager


# Create your models here.
class User(AbstractBaseUser):
    GENDER_CHOICES = [
        ("male", "Male"),
        ("female", "Female"),
        ("other", "Other"),
    ]

    USER_STATUS = [
        ("verified", "Verified"),
        ("unverified", "Unverified"),
    ]

    id = models.UUIDField(primary_key=True, default=uuid4, editable=False)
    google_id = models.CharField(max_length=255, blank=True, null=True)
    apple_id = models.CharField(max_length=255, blank=True, null=True)
    full_name = models.CharField(max_length=100)
    gender = models.CharField(max_length=10, choices=GENDER_CHOICES, default="other")
    age = models.PositiveIntegerField(blank=True, null=True)
    photo_url = models.URLField(max_length=255, blank=True, null=True)
    email = models.EmailField(max_length=255, unique=True)
    phone_number = models.CharField(max_length=15, blank=True, null=True)
    status = models.CharField(max_length=10, choices=USER_STATUS, default="unverified")
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    is_admin = models.BooleanField(default=False)

    USERNAME_FIELD = "email"
    REQUIRED_FIELDS = ["full_name"]

    objects = UserManager()

    def __str__(self):
        return self.full_name

    def get_short_name(self):
        return self.full_name.split(" ")[-1]

    def has_perm(self, perm, obj=None):
        return True

    def has_module_perms(self, app_label):
        return True

    @property
    def is_staff(self):
        return self.is_admin
