from django.contrib import admin
from .models.transaction import Transaction
from .models.detail import TransactionDetail


# Register your models here.
class TransactionAdmin(admin.ModelAdmin):
    list_display = [
        "wallet",
        "type",
        "amount",
        "transaction_date",
        "created_at",
        "updated_at",
    ]
    search_fields = ["wallet__user__full_name", "type", "amount"]
    list_filter = ["type", "transaction_date", "created_at", "updated_at"]
    filter_horizontal = (
        "labels",
    )  # This allows for a better UI to manage ManyToManyField

    class Meta:
        model = Transaction


class TransactionDetailAdmin(admin.ModelAdmin):
    list_display = [
        "transaction",
        "item_name",
        "item_price",
        "created_at",
        "updated_at",
    ]
    search_fields = ["transaction"]
    list_filter = ["created_at", "updated_at"]

    class Meta:
        model = TransactionDetail


admin.site.register(Transaction, TransactionAdmin)
admin.site.register(TransactionDetail, TransactionDetailAdmin)
