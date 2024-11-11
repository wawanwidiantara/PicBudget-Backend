from rest_framework import serializers
from django.contrib.auth import get_user_model
from django.core.exceptions import ValidationError
from picbudget.authentication.models import OTP
from picbudget.authentication.utils import send_otp_email

User = get_user_model()


class RegisterSerializer(serializers.Serializer):
    email = serializers.EmailField()
    password = serializers.CharField(write_only=True)

    def validate_email(self, value):
        user = User.objects.filter(email=value).first()
        if user:
            if user.status == "verified":
                raise ValidationError(
                    "A user with this email already exists and is verified."
                )
        return value

    def create(self, validated_data):
        email = validated_data["email"]
        password = validated_data["password"]
        user, created = User.objects.get_or_create(email=email)
        if created or user.status == "unverified":
            user.set_password(password)
            user.status = "unverified"
            user.save()

            # Generate OTP
            otp_instance, _ = OTP.objects.get_or_create(user=user)
            otp_code = otp_instance.generate_otp()

            # Send OTP to email (pseudo-code, replace with actual email sending logic)
            send_otp_email(user.email, otp_code)

        return user


class RegisterPersonalDataSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ["full_name", "gender", "age", "phone_number", "photo_url"]

    def update(self, instance, validated_data):
        instance.full_name = validated_data.get("full_name", instance.full_name)
        instance.gender = validated_data.get("gender", instance.gender)
        instance.age = validated_data.get("age", instance.age)
        instance.phone_number = validated_data.get(
            "phone_number", instance.phone_number
        )
        instance.photo_url = validated_data.get("photo_url", instance.photo_url)
        instance.save()
        return instance