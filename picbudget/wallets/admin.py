from django.contrib import admin
from .models.wallet import Wallet


class WalletAdmin(admin.ModelAdmin):
    list_display = ["name", "user", "balance", "created_at", "updated_at"]
    search_fields = ["name"]
    list_filter = ["created_at", "updated_at"]

    class Meta:
        model = Wallet


# Register your models here.
admin.site.register(Wallet, WalletAdmin)
