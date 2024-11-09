from django.contrib import admin

# Register your models here.
from .models.membership import Membership
from .models.payment import Payment

admin.site.register(Membership)
admin.site.register(Payment)
