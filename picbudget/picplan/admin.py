from django.contrib import admin
from .models import Plan


class PlanAdmin(admin.ModelAdmin):
    list_display = [
        "name",
        "amount",
        "period",
        "created_at",
        "updated_at",
    ]
    search_fields = ["name"]
    list_filter = ["created_at", "updated_at"]

    class Meta:
        model = Plan


admin.site.register(Plan, PlanAdmin)
