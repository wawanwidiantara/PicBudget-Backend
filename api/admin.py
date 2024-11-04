from django.contrib import admin

# Register your models here.
from .models import User, Wallet, Transaction, TransactionItem

# Register your models here.
admin.site.register(User)
admin.site.register(Wallet)
admin.site.register(Transaction)
admin.site.register(TransactionItem)
