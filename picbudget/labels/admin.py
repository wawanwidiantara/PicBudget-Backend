from django.contrib import admin
from .models import Label


# Register your models here.
class LabelAdmin(admin.ModelAdmin):
    list_display = ("name", "emoticon", "created_at", "updated_at")
    list_filter = ("created_at", "updated_at")
    search_fields = ("name",)
    ordering = ("created_at",)

    class Meta:
        model = Label


admin.site.register(Label, LabelAdmin)
