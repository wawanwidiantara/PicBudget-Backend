from rest_framework import serializers
from picbudget.authentication.models import OTP
from django.contrib.auth import get_user_model
from django.core.exceptions import ValidationError
from picbudget.project.task import send_email_task

User = get_user_model()


class OTPSerializer(serializers.Serializer):
    email = serializers.EmailField()

    def create(self, validated_data):
        email = validated_data["email"]
        user = User.objects.get(email=email)
        otp_instance, _ = OTP.objects.get_or_create(user=user)
        otp_code = otp_instance.generate_otp()

        subject = "Your OTP Code"
        message = f"Your OTP code is {otp_code}. It will expire in 5 minutes."
        recipient_list = [user.email]
        send_email_task.delay(subject, message, recipient_list)

        return otp_instance


class VerifyOTPSerializer(serializers.Serializer):
    email = serializers.EmailField()
    otp_code = serializers.CharField(max_length=6)

    def validate(self, data):
        email = data.get("email")
        otp_code = data.get("otp_code")

        try:
            user = User.objects.get(email=email)
            otp_instance = OTP.objects.get(user=user)
        except (User.DoesNotExist, OTP.DoesNotExist):
            raise ValidationError("Invalid email or OTP code.")

        if not otp_instance.validate_otp(otp_code):
            raise ValidationError("Invalid or expired OTP code.")

        return data

    def create(self, validated_data):
        email = validated_data["email"]
        user = User.objects.get(email=email)
        user.status = "verified"
        user.save()
        return user
