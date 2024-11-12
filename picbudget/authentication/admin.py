from django.contrib import admin
from .models import OTP


class OTPAdmin(admin.ModelAdmin):
    list_display = ["get_user_email", "otp"]

    def get_user_email(self, obj):
        return obj.user.email

    get_user_email.short_description = "Email"  # Set the column header to "Email"

    class Meta:
        model = OTP


admin.site.register(OTP, OTPAdmin)
