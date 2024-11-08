from django.contrib import admin

# Register your models here.
from .models.membership import Membership

admin.site.register(Membership)
