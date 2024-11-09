from django.contrib import admin

from .models import User


class UserAdmin(admin.ModelAdmin):
    list_display = ("full_name", "email", "is_admin", "created_at", "updated_at")
    list_filter = ("is_admin", "created_at", "updated_at")
    search_fields = ("full_name", "email")
    ordering = ("created_at",)

    class Meta:
        model = User


admin.site.register(User, UserAdmin)
